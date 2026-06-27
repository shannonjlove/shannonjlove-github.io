#!/usr/bin/env python3
"""
MediaFire → inbox-idrive-e2/01001-uploads/mediafire/
Uses MediaFire REST API (rclone has no MediaFire backend).

Env vars required:
    MEDIAFIRE_EMAIL     — MediaFire account email
    MEDIAFIRE_PASSWORD  — MediaFire account password

Optional:
    MEDIAFIRE_APP_ID    — MediaFire app ID (defaults to public API key)
    MEDIAFIRE_API_KEY   — MediaFire API key

iDrive E2 credentials are read from rclone config (idrive-primary) or env:
    IDRIVE_ACCESS_KEY, IDRIVE_SECRET_KEY, IDRIVE_ENDPOINT
"""
import os, sys, json, time, hashlib, logging
import requests
import boto3
from botocore.config import Config

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
log = logging.getLogger("mediafire-sync")

# ── Config ──────────────────────────────────────────────────────────────────

MF_EMAIL    = os.environ.get("MEDIAFIRE_EMAIL", "")
MF_PASS     = os.environ.get("MEDIAFIRE_PASSWORD", "")
MF_APP_ID   = os.environ.get("MEDIAFIRE_APP_ID", "")
MF_API_KEY  = os.environ.get("MEDIAFIRE_API_KEY", "")
MF_API_BASE = "https://www.mediafire.com/api/1.5"

IDRIVE_ENDPOINT   = os.environ.get("IDRIVE_ENDPOINT", "https://p3h2.va.idrivee2-48.com")
IDRIVE_ACCESS_KEY = os.environ.get("IDRIVE_ACCESS_KEY", "hNOOh0odHmPwKt9xDbll")
IDRIVE_SECRET_KEY = os.environ.get("IDRIVE_SECRET_KEY", "w8X3Ubjfp6rnGzjoFjBv1kwpdMpn9MxzbQcjozA6")
IDRIVE_CA         = "/root/.ccr/ca-bundle.crt"

INBOX_BUCKET = "inbox-idrive-e2"
INBOX_PREFIX = "01001-uploads/mediafire/"

# ── MediaFire Authentication ────────────────────────────────────────────────

def mf_get_session_token():
    """Authenticate with MediaFire and return session token."""
    if not MF_EMAIL or not MF_PASS:
        log.error("MEDIAFIRE_EMAIL and MEDIAFIRE_PASSWORD must be set")
        sys.exit(1)

    # MediaFire signature: sha1(email + password + app_id + api_key) if api_key present
    # otherwise sha1(email + password + app_id)
    if MF_API_KEY:
        sig_str = MF_EMAIL + MF_PASS + MF_APP_ID + MF_API_KEY
    else:
        sig_str = MF_EMAIL + MF_PASS + MF_APP_ID
    sig = hashlib.sha1(sig_str.encode()).hexdigest() if MF_APP_ID else ""

    params = {
        "email": MF_EMAIL,
        "password": MF_PASS,
        "application_id": MF_APP_ID,
        "response_format": "json",
    }
    if sig:
        params["signature"] = sig

    r = requests.post(f"{MF_API_BASE}/user/get_session_token.php", data=params, timeout=30)
    data = r.json()

    if data.get("response", {}).get("result") != "Success":
        err = data.get("response", {}).get("message", "Unknown error")
        # If 2FA required, MediaFire sends code to email/SMS
        if "tfa" in err.lower() or "two" in err.lower():
            code = input("MediaFire 2FA code: ").strip()
            params["tfa_code"] = code
            r2 = requests.post(f"{MF_API_BASE}/user/get_session_token.php", data=params, timeout=30)
            data = r2.json()
            if data.get("response", {}).get("result") != "Success":
                log.error(f"MediaFire auth failed: {data.get('response',{}).get('message')}")
                sys.exit(1)
        else:
            log.error(f"MediaFire auth failed: {err}")
            sys.exit(1)

    token = data["response"]["session_token"]
    log.info(f"MediaFire authenticated (token: {token[:8]}...)")
    return token


def mf_list_folder(session_token, folder_key="", page=1):
    """List files in a MediaFire folder."""
    params = {
        "session_token": session_token,
        "folder_key": folder_key,
        "chunk": page,
        "chunk_size": 100,
        "response_format": "json",
    }
    r = requests.get(f"{MF_API_BASE}/folder/get_content.php", params=params, timeout=30)
    return r.json()


def mf_get_all_files(session_token, folder_key="", path_prefix=""):
    """Recursively enumerate all files in MediaFire."""
    files = []
    page = 1
    while True:
        data = mf_list_folder(session_token, folder_key, page)
        content = data.get("response", {}).get("folder_content", {})

        # Files in this folder
        for f in content.get("files", []):
            files.append({
                "name": f.get("filename", ""),
                "key": f.get("quickkey", ""),
                "size": int(f.get("size", 0)),
                "links": f.get("links", {}),
                "path": path_prefix + "/" + f.get("filename", "") if path_prefix else f.get("filename", ""),
            })

        # Recurse into subfolders
        for d in content.get("folders", []):
            subfolder_path = path_prefix + "/" + d.get("name", "") if path_prefix else d.get("name", "")
            files.extend(mf_get_all_files(session_token, d.get("folderkey", ""), subfolder_path))

        # Check pagination
        more_chunks = content.get("more_chunks", "no")
        if more_chunks == "no":
            break
        page += 1

    return files


# ── S3 Upload ────────────────────────────────────────────────────────────────

def get_s3_client():
    verify = IDRIVE_CA if os.path.exists(IDRIVE_CA) else True
    return boto3.client(
        "s3",
        endpoint_url=IDRIVE_ENDPOINT,
        aws_access_key_id=IDRIVE_ACCESS_KEY,
        aws_secret_access_key=IDRIVE_SECRET_KEY,
        region_name="us-east-1",
        verify=verify,
        config=Config(signature_version="s3v4"),
    )


def s3_key_exists(s3, key):
    try:
        s3.head_object(Bucket=INBOX_BUCKET, Key=key)
        return True
    except s3.exceptions.ClientError:
        return False


def upload_to_inbox(s3, file_info):
    """Download from MediaFire and stream upload to iDrive E2 inbox."""
    dest_key = INBOX_PREFIX + file_info["path"]

    if s3_key_exists(s3, dest_key):
        log.info(f"SKIP (exists): {dest_key}")
        return False

    # Get direct download link
    links = file_info.get("links", {})
    dl_url = links.get("normal_download", "") or links.get("download", "")

    if not dl_url:
        log.warning(f"SKIP (no download link): {file_info['name']}")
        return False

    log.info(f"UPLOAD: {file_info['path']} → {dest_key} ({file_info['size']} bytes)")

    try:
        with requests.get(dl_url, stream=True, timeout=60) as r:
            r.raise_for_status()
            s3.upload_fileobj(
                r.raw,
                INBOX_BUCKET,
                dest_key,
                ExtraArgs={"Metadata": {"source": "mediafire", "original-path": file_info["path"]}},
            )
        return True
    except Exception as e:
        log.error(f"UPLOAD FAILED: {file_info['path']} — {e}")
        return False


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    log.info("MediaFire inbox sync starting")

    if not MF_EMAIL:
        log.error("Set MEDIAFIRE_EMAIL and MEDIAFIRE_PASSWORD environment variables")
        sys.exit(1)

    session_token = mf_get_session_token()
    s3 = get_s3_client()

    log.info("Enumerating MediaFire files...")
    all_files = mf_get_all_files(session_token)
    log.info(f"Found {len(all_files)} files in MediaFire")

    uploaded = skipped = errors = 0
    for f in all_files:
        result = upload_to_inbox(s3, f)
        if result is True:
            uploaded += 1
        elif result is False:
            skipped += 1
        else:
            errors += 1

    log.info(f"MediaFire sync complete: {uploaded} uploaded, {skipped} skipped, {errors} errors")
    return errors == 0


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
