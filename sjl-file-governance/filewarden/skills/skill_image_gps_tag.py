"""
Skill: Image GPS → Location Tag
Origin: Hazel "Auto tag Images with address location via EXIF GPS data"
SJL Stage: analyze (post-hook)

Extracts GPS coordinates from image EXIF using ExifTool,
resolves address via reverse geocoding API (configurable: Google, Nominatim),
and writes the location as EXIF keywords and as SJL metadata.
Nominatim (OpenStreetMap) is the privacy-respecting default (no API key needed).
"""

from __future__ import annotations

import json
import logging
import subprocess
import urllib.request
import urllib.parse
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from filewarden.core.pipeline import Transaction, skill

log = logging.getLogger("filewarden.skills.image_gps_tag")

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".tiff", ".tif", ".heic", ".heif", ".png"}


def _get_gps_exiftool(path: Path) -> Optional[Tuple[float, float]]:
    """Extract GPS lat/lon using ExifTool. Returns (lat, lon) decimal or None."""
    try:
        result = subprocess.run(
            [
                "exiftool",
                "-n",                   # Use decimal GPS values directly
                "-GPSLatitude",
                "-GPSLongitude",
                "-GPSLatitudeRef",
                "-GPSLongitudeRef",
                "-j",                   # JSON output
                str(path),
            ],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode != 0:
            return None
        data = json.loads(result.stdout)
        if not data:
            return None
        record = data[0]
        lat = record.get("GPSLatitude")
        lon = record.get("GPSLongitude")
        lat_ref = record.get("GPSLatitudeRef", "N")
        lon_ref = record.get("GPSLongitudeRef", "E")
        if lat is None or lon is None:
            return None
        if lat_ref == "S":
            lat = -abs(lat)
        if lon_ref == "W":
            lon = -abs(lon)
        return (float(lat), float(lon))
    except (FileNotFoundError, json.JSONDecodeError, subprocess.TimeoutExpired, KeyError):
        return None


def _reverse_geocode_nominatim(lat: float, lon: float) -> Optional[Dict]:
    """
    Reverse geocode using OpenStreetMap Nominatim (no API key required).
    Privacy-respecting alternative to Google Geocoding API.
    """
    url = (
        f"https://nominatim.openstreetmap.org/reverse"
        f"?format=json&lat={lat}&lon={lon}&zoom=18&addressdetails=1"
    )
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "SJL-FileWarden/2.0 (sjlove@shannonjeffreylove.com)"}
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read())
    except Exception as e:
        log.warning("Nominatim geocoding failed: %s", e)
        return None


def _reverse_geocode_google(lat: float, lon: float, api_key: str) -> Optional[Dict]:
    """Google Geocoding API (requires API key)."""
    url = (
        f"https://maps.googleapis.com/maps/api/geocode/json"
        f"?latlng={lat},{lon}&result_type=street_address&key={api_key}"
    )
    try:
        with urllib.request.urlopen(url, timeout=15) as resp:
            data = json.loads(resp.read())
            if data.get("results"):
                return data["results"][0]
    except Exception as e:
        log.warning("Google geocoding failed: %s", e)
    return None


def _format_location(geo_result: Dict, provider: str) -> Dict[str, str]:
    """Extract standardized location fields from geocoding result."""
    if provider == "nominatim":
        address = geo_result.get("address", {})
        return {
            "full_address": geo_result.get("display_name", ""),
            "city": address.get("city") or address.get("town") or address.get("village", ""),
            "state": address.get("state", ""),
            "country": address.get("country", ""),
            "postcode": address.get("postcode", ""),
        }
    else:  # Google
        components = {
            c["types"][0]: c["long_name"]
            for c in geo_result.get("address_components", [])
            if c.get("types")
        }
        return {
            "full_address": geo_result.get("formatted_address", ""),
            "city": components.get("locality", ""),
            "state": components.get("administrative_area_level_1", ""),
            "country": components.get("country", ""),
            "postcode": components.get("postal_code", ""),
        }


def _write_exif_keywords(path: Path, keywords: list[str]) -> None:
    """Write location keywords back to EXIF using ExifTool."""
    try:
        kw_args = []
        for kw in keywords:
            kw_args.extend([f"-keywords+={kw}"])
        subprocess.run(
            ["exiftool", "-overwrite_original_in_place", "-P"] + kw_args + [str(path)],
            capture_output=True, timeout=15
        )
    except (FileNotFoundError, subprocess.TimeoutExpired) as e:
        log.debug("ExifTool keyword write failed: %s", e)


@skill(stage="analyze", when="post", name="image_gps_tag")
def tag_image_with_location(tx: Transaction, config: Dict[str, Any]) -> None:
    """
    Extract GPS EXIF from image, reverse geocode, write location keywords.
    """
    path = tx.original_path
    if path.suffix.lower() not in IMAGE_EXTENSIONS:
        return

    if not config.get("image_gps_tag_enabled", True):
        return

    coords = _get_gps_exiftool(path)
    if not coords:
        log.debug("No GPS data in %s", path.name)
        return

    lat, lon = coords
    provider = config.get("geocoding_provider", "nominatim")
    geo_result = None

    if provider == "google":
        api_key = config.get("google_geocoding_api_key", "")
        if api_key:
            geo_result = _reverse_geocode_google(lat, lon, api_key)

    if not geo_result:
        geo_result = _reverse_geocode_nominatim(lat, lon)
        provider = "nominatim"

    if not geo_result:
        return

    location = _format_location(geo_result, provider)
    tx.metadata["gps_location"] = location
    tx.metadata["gps_coordinates"] = {"lat": lat, "lon": lon}

    # Write location as EXIF keywords
    keywords = [v for v in [location["city"], location["state"], location["country"]] if v]
    if keywords:
        _write_exif_keywords(path, keywords)

    # Update semantic title with location if enabled
    if config.get("image_gps_tag_use_in_title", False) and location.get("city"):
        city_slug = location["city"].lower().replace(" ", "-")
        tx.semantic_title = f"{city_slug}-photo"

    tx.skill_outputs["image_gps_tag"] = {
        "coordinates": f"{lat},{lon}",
        "location": location,
        "keywords_written": keywords,
    }
    log.info("GPS tagged %s: %s", path.name, location.get("full_address", "")[:60])
