#!/usr/bin/env python3
"""
iDrive S3 Cloud Bridge
Sync files between an iDrive S3 bucket and Dropbox, pCloud, or iCloud Drive.

Usage:
    cp .env.example .env && fill in credentials
    source .env
    python bridge.py list
    python bridge.py sync-to dropbox --s3-prefix photos/ --cloud-folder /Photos
    python bridge.py sync-from pcloud --cloud-folder /Backups --s3-prefix backups/
"""

import io
import os
import sys
import argparse
from typing import Iterator

import boto3
from botocore.config import Config as BotoConfig

PROVIDERS = ["dropbox", "pcloud", "icloud"]


# ── iDrive S3 ──────────────────────────────────────────────────────────────

class S3Client:
    def __init__(self):
        for var in ("IDRIVE_S3_ENDPOINT", "IDRIVE_S3_ACCESS_KEY",
                    "IDRIVE_S3_SECRET_KEY", "IDRIVE_S3_BUCKET"):
            if not os.environ.get(var):
                _die(f"Missing required env var: {var}")
        self.client = boto3.client(
            "s3",
            endpoint_url=os.environ["IDRIVE_S3_ENDPOINT"],
            aws_access_key_id=os.environ["IDRIVE_S3_ACCESS_KEY"],
            aws_secret_access_key=os.environ["IDRIVE_S3_SECRET_KEY"],
            config=BotoConfig(signature_version="s3v4"),
        )
        self.bucket = os.environ["IDRIVE_S3_BUCKET"]

    def list_objects(self, prefix: str = "") -> Iterator[dict]:
        paginator = self.client.get_paginator("list_objects_v2")
        for page in paginator.paginate(Bucket=self.bucket, Prefix=prefix):
            for obj in page.get("Contents", []):
                yield obj

    def download(self, key: str) -> bytes:
        obj = self.client.get_object(Bucket=self.bucket, Key=key)
        return obj["Body"].read()

    def upload(self, key: str, data: bytes) -> None:
        self.client.put_object(Bucket=self.bucket, Key=key, Body=data)

    def delete(self, key: str) -> None:
        self.client.delete_object(Bucket=self.bucket, Key=key)


# ── Dropbox ────────────────────────────────────────────────────────────────

class DropboxBridge:
    def __init__(self):
        try:
            import dropbox as _dbx
        except ImportError:
            _die("dropbox package not installed — run: pip install dropbox")
        token = os.environ.get("DROPBOX_ACCESS_TOKEN")
        if not token:
            _die("Missing required env var: DROPBOX_ACCESS_TOKEN")
        self._dbx = _dbx.Dropbox(token)

    def list_files(self, folder: str = "") -> Iterator[dict]:
        import dropbox.files as dbf
        # Dropbox root is "" not "/"
        path = "" if folder in ("/", "") else folder.rstrip("/")
        result = self._dbx.files_list_folder(path, recursive=True)
        while True:
            for entry in result.entries:
                if isinstance(entry, dbf.FileMetadata):
                    yield {
                        "key": entry.path_lower,
                        "size": entry.size,
                        "content_hash": entry.content_hash,
                    }
            if not result.has_more:
                break
            result = self._dbx.files_list_folder_continue(result.cursor)

    def download(self, path: str) -> bytes:
        _, response = self._dbx.files_download(path)
        return response.content

    def upload(self, path: str, data: bytes) -> None:
        import dropbox.files as dbf
        self._dbx.files_upload(data, path, mode=dbf.WriteMode.overwrite)

    def delete(self, path: str) -> None:
        self._dbx.files_delete_v2(path)


# ── pCloud ─────────────────────────────────────────────────────────────────

class PCloudBridge:
    def __init__(self):
        try:
            import requests as _req  # noqa: F401
        except ImportError:
            _die("requests package not installed — run: pip install requests")
        import requests
        self._requests = requests
        token = os.environ.get("PCLOUD_ACCESS_TOKEN")
        if not token:
            _die("Missing required env var: PCLOUD_ACCESS_TOKEN")
        self.token = token
        region = os.environ.get("PCLOUD_REGION", "us").lower()
        self.base = "https://eapi.pcloud.com" if region == "eu" else "https://api.pcloud.com"

    def _api(self, method: str, **params) -> dict:
        params["access_token"] = self.token
        r = self._requests.get(f"{self.base}/{method}", params=params, timeout=30)
        r.raise_for_status()
        data = r.json()
        if data.get("result", 0) != 0:
            raise RuntimeError(f"pCloud {method} error {data['result']}: {data.get('error')}")
        return data

    def list_files(self, folder: str = "/") -> Iterator[dict]:
        data = self._api("listfolder", path=folder, recursive=1)

        def _walk(meta: dict):
            for item in meta.get("contents", []):
                if item.get("isfolder"):
                    yield from _walk(item)
                else:
                    yield {"key": item["path"], "size": item.get("size", 0), "fileid": item["fileid"]}

        yield from _walk(data["metadata"])

    def download(self, path: str) -> bytes:
        link_data = self._api("getfilelink", path=path)
        host = link_data["hosts"][0]
        url = f"https://{host}{link_data['path']}"
        r = self._requests.get(url, timeout=120)
        r.raise_for_status()
        return r.content

    def upload(self, folder: str, filename: str, data: bytes) -> None:
        params = {"access_token": self.token, "path": folder, "filename": filename}
        r = self._requests.post(
            f"{self.base}/uploadfile",
            params=params,
            files={"file": (filename, data)},
            timeout=120,
        )
        r.raise_for_status()
        result = r.json()
        if result.get("result", 0) != 0:
            raise RuntimeError(f"pCloud upload error {result['result']}: {result.get('error')}")

    def delete(self, path: str) -> None:
        self._api("deletefile", path=path)


# ── iCloud ─────────────────────────────────────────────────────────────────

class ICloudBridge:
    def __init__(self):
        try:
            from pyicloud import PyiCloudService
        except ImportError:
            _die("pyicloud not installed — run: pip install pyicloud")
        apple_id = os.environ.get("ICLOUD_APPLE_ID")
        password = os.environ.get("ICLOUD_PASSWORD")
        if not apple_id or not password:
            _die("Missing required env vars: ICLOUD_APPLE_ID and ICLOUD_PASSWORD")
        print("Connecting to iCloud…")
        self.api = PyiCloudService(apple_id, password)
        if self.api.requires_2fa:
            code = input("Enter the 6-digit 2FA code sent to your Apple device: ").strip()
            if not self.api.validate_2fa_code(code):
                _die("Invalid 2FA code")
            self.api.trust_session()
        elif self.api.requires_2sa:
            devices = self.api.trusted_devices
            for i, dev in enumerate(devices):
                print(f"  [{i}] {dev.get('deviceName', 'Unknown')}")
            idx = int(input("Select device for 2SA: "))
            device = devices[idx]
            if not self.api.send_verification_code(device):
                _die("Failed to send verification code")
            code = input("Enter the verification code: ").strip()
            if not self.api.validate_verification_code(device, code):
                _die("Invalid verification code")
        self.drive = self.api.drive

    def _node_at(self, path: str):
        parts = [p for p in path.strip("/").split("/") if p]
        node = self.drive
        for part in parts:
            node = node[part]
        return node

    def list_files(self, folder: str = "/") -> Iterator[dict]:
        def _walk(node, base_path: str):
            try:
                for name in node.dir():
                    child = node[name]
                    child_path = f"{base_path.rstrip('/')}/{name}"
                    if child.type == "folder":
                        yield from _walk(child, child_path)
                    else:
                        yield {"key": child_path, "size": child.size or 0}
            except Exception as exc:
                print(f"  [warn] Could not list {base_path}: {exc}", file=sys.stderr)

        root = self._node_at(folder)
        yield from _walk(root, folder)

    def download(self, path: str) -> bytes:
        node = self._node_at(path)
        return node.open(stream=True).content

    def upload(self, folder: str, filename: str, data: bytes) -> None:
        node = self._node_at(folder)
        node.upload(io.BytesIO(data), filename)

    def delete(self, path: str) -> None:
        self._node_at(path).delete()


# ── Sync helpers ───────────────────────────────────────────────────────────

def _get_provider(name: str):
    return {"dropbox": DropboxBridge, "pcloud": PCloudBridge, "icloud": ICloudBridge}[name]()


def _cloud_upload(provider, provider_name: str, cloud_path: str, data: bytes) -> None:
    if provider_name == "dropbox":
        provider.upload(cloud_path, data)
    else:
        folder = "/".join(cloud_path.split("/")[:-1]) or "/"
        filename = cloud_path.split("/")[-1]
        provider.upload(folder, filename, data)


def _die(msg: str) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(1)


def _fmt_size(n: int) -> str:
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} PB"


# ── Commands ───────────────────────────────────────────────────────────────

def cmd_list(args):
    s3 = S3Client()
    print(f"\n  iDrive S3 — bucket: {s3.bucket}  prefix: '{args.prefix}'\n")
    total, count = 0, 0
    for obj in s3.list_objects(args.prefix):
        print(f"  {obj['Key']:<70}  {_fmt_size(obj['Size']):>10}")
        total += obj["Size"]
        count += 1
    print(f"\n  {count} objects, {_fmt_size(total)} total\n")


def cmd_sync_to(args):
    s3 = S3Client()
    provider = _get_provider(args.provider)
    cloud_folder = (args.cloud_folder or "/").rstrip("/") or "/"
    s3_prefix = args.s3_prefix or ""

    print(f"\n  Sync: iDrive S3 (prefix='{s3_prefix}') → {args.provider} ({cloud_folder})\n")

    cloud_index = {f["key"]: f for f in provider.list_files(cloud_folder)}
    xfer, skip, err = 0, 0, 0

    for obj in s3.list_objects(s3_prefix):
        key = obj["Key"]
        relative = key[len(s3_prefix):].lstrip("/") if s3_prefix else key
        cloud_path = f"{cloud_folder}/{relative}"

        existing = cloud_index.get(cloud_path)
        if existing and existing["size"] == obj["Size"]:
            skip += 1
            continue

        try:
            print(f"  → {key}  ({_fmt_size(obj['Size'])})")
            data = s3.download(key)
            _cloud_upload(provider, args.provider, cloud_path, data)
            xfer += 1
        except Exception as exc:
            print(f"    [error] {exc}", file=sys.stderr)
            err += 1

    print(f"\n  Done — {xfer} transferred, {skip} skipped, {err} errors\n")


def cmd_sync_from(args):
    s3 = S3Client()
    provider = _get_provider(args.provider)
    cloud_folder = (args.cloud_folder or "/").rstrip("/") or "/"
    s3_prefix = args.s3_prefix or ""

    print(f"\n  Sync: {args.provider} ({cloud_folder}) → iDrive S3 (prefix='{s3_prefix}')\n")

    s3_index = {obj["Key"]: obj for obj in s3.list_objects(s3_prefix)}
    xfer, skip, err = 0, 0, 0

    for f in provider.list_files(cloud_folder):
        relative = f["key"].lstrip("/")
        s3_key = f"{s3_prefix.rstrip('/')}/{relative}" if s3_prefix else relative

        existing = s3_index.get(s3_key)
        if existing and existing["Size"] == f["size"]:
            skip += 1
            continue

        try:
            print(f"  ← {f['key']}  ({_fmt_size(f['size'])})")
            data = provider.download(f["key"])
            s3.upload(s3_key, data)
            xfer += 1
        except Exception as exc:
            print(f"    [error] {exc}", file=sys.stderr)
            err += 1

    print(f"\n  Done — {xfer} transferred, {skip} skipped, {err} errors\n")


def cmd_list_cloud(args):
    provider = _get_provider(args.provider)
    folder = args.folder or "/"
    print(f"\n  {args.provider} — folder: {folder}\n")
    total, count = 0, 0
    for f in provider.list_files(folder):
        print(f"  {f['key']:<70}  {_fmt_size(f['size']):>10}")
        total += f["size"]
        count += 1
    print(f"\n  {count} files, {_fmt_size(total)} total\n")


# ── Entry point ────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Bridge iDrive S3 ↔ Dropbox / pCloud / iCloud Drive",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
examples:
  python bridge.py list
  python bridge.py list-cloud dropbox
  python bridge.py list-cloud pcloud --folder /Photos
  python bridge.py sync-to dropbox --s3-prefix videos/ --cloud-folder /Videos
  python bridge.py sync-to pcloud --cloud-folder /Backups
  python bridge.py sync-from dropbox --cloud-folder /Camera --s3-prefix phone/
  python bridge.py sync-from icloud --cloud-folder /Documents --s3-prefix docs/
        """,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # list (S3)
    p_ls = sub.add_parser("list", help="List objects in your iDrive S3 bucket")
    p_ls.add_argument("--prefix", default="", help="Filter by key prefix")

    # list-cloud
    p_lc = sub.add_parser("list-cloud", help="List files in cloud provider")
    p_lc.add_argument("provider", choices=PROVIDERS)
    p_lc.add_argument("--folder", default="/", help="Cloud folder to list")

    # sync-to  (S3 → cloud)
    p_to = sub.add_parser("sync-to", help="Copy iDrive S3 objects → cloud provider")
    p_to.add_argument("provider", choices=PROVIDERS)
    p_to.add_argument("--s3-prefix", default="", metavar="PREFIX",
                      help="Only sync S3 objects under this prefix")
    p_to.add_argument("--cloud-folder", default="/", metavar="FOLDER",
                      help="Destination folder in cloud provider (default: /)")

    # sync-from  (cloud → S3)
    p_fr = sub.add_parser("sync-from", help="Copy cloud provider files → iDrive S3")
    p_fr.add_argument("provider", choices=PROVIDERS)
    p_fr.add_argument("--cloud-folder", default="/", metavar="FOLDER",
                      help="Source folder in cloud provider (default: /)")
    p_fr.add_argument("--s3-prefix", default="", metavar="PREFIX",
                      help="Store files under this S3 key prefix")

    args = parser.parse_args()
    dispatch = {
        "list": cmd_list,
        "list-cloud": cmd_list_cloud,
        "sync-to": cmd_sync_to,
        "sync-from": cmd_sync_from,
    }
    dispatch[args.command](args)


if __name__ == "__main__":
    main()
