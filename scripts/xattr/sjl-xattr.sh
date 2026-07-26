#!/usr/bin/env bash
# =============================================================================
# SJL XATTR LIBRARY — Shannon J. Love | shannonjlove.cloud
#
# Writes SJL metadata fields as extended attributes and JSON sidecars.
# Source this file in any SJL script:  source /path/to/sjl-xattr.sh
#
# Persistence strategy (three-layer fallback):
#   1. XMP-SJL embedded fields via ExifTool  →  most persistent; survives all
#      cloud syncs that preserve file content (GDrive, Dropbox, pCloud, iCloud)
#   2. Extended attributes (xattrs)          →  macOS: com.apple.metadata + custom
#                                               Linux: user.sjl.*
#                                               WARNING: stripped by most clouds;
#                                               iCloud preserves via AppleDouble
#   3. JSON sidecar (<file>.sjl.json)        →  cloud-resilient; plain text file;
#      survives all cloud services; travels with the file
#
# Usage:
#   source sjl-xattr.sh
#   sjl_xattr_write_core  FILE uuid24 para cloud project processed
#   sjl_xattr_write_field FILE SJLgenre "R&B"
#   sjl_sidecar_write     FILE <json-string>
#   sjl_sidecar_from_exif FILE                   # build sidecar from ExifTool output
#
# Dependencies:
#   macOS: xattr (built-in), plutil (built-in), exiftool
#   Linux: attr package (setfattr/getfattr), exiftool
#   Both:  python3 or jq (for JSON sidecar generation)
# =============================================================================

# =============================================================================
# PLATFORM DETECTION
# =============================================================================

_SJL_OS="$(uname -s)"
_SJL_EXIFTOOL="${EXIFTOOL_BIN:-exiftool}"
_SJL_EXIFTOOL_CONFIG="${SJL_EXIFTOOL_CONFIG:-$HOME/.ExifTool_config}"

sjl_is_mac()   { [[ "$_SJL_OS" == "Darwin" ]]; }
sjl_is_linux() { [[ "$_SJL_OS" == "Linux" ]]; }

# =============================================================================
# LOW-LEVEL XATTR PRIMITIVES
# =============================================================================

# _sjl_xattr_set FILE ATTR_NAME VALUE
# Writes a single xattr. On macOS uses xattr; on Linux uses setfattr.
_sjl_xattr_set() {
    local file="$1" attr="$2" value="$3"
    [[ -z "$value" ]] && return 0
    if sjl_is_mac; then
        xattr -w "$attr" "$value" "$file" 2>/dev/null || true
    else
        setfattr -n "$attr" -v "$value" "$file" 2>/dev/null || true
    fi
}

# _sjl_xattr_get FILE ATTR_NAME
_sjl_xattr_get() {
    local file="$1" attr="$2"
    if sjl_is_mac; then
        xattr -p "$attr" "$file" 2>/dev/null || true
    else
        getfattr -n "$attr" --only-values "$file" 2>/dev/null || true
    fi
}

# _sjl_xattr_set_plist FILE KMDITEM_ATTR VALUE
# Sets a macOS Spotlight kMDItem xattr using a properly-typed plist.
# Most kMDItem keys expect a plist value, not raw string.
_sjl_xattr_set_plist() {
    local file="$1" attr="$2" value="$3"
    [[ -z "$value" ]] && return 0
    if ! sjl_is_mac; then return 0; fi
    # Write as plist string
    local plist
    plist=$(python3 -c "
import plistlib, sys
d = plistlib.dumps('$value'.encode().decode(), fmt=plistlib.FMT_BINARY)
sys.stdout.buffer.write(d)
" 2>/dev/null) || return 0
    printf '%s' "$plist" | xattr -w "$attr" /dev/stdin "$file" 2>/dev/null || true
}

# =============================================================================
# SJL FIELD → XATTR NAMESPACE MAP
# =============================================================================
# Each SJL field maps to:
#   macOS primary  = com.apple.metadata:kMDItem* (Spotlight-indexed)
#   macOS fallback = com.shannonjlove.sjl.* (private namespace)
#   Linux          = user.sjl.* (POSIX xattr)
#
# This function writes BOTH macOS namespaces and the Linux namespace in one call
# so a file processed on one platform already has attrs the other can read.

# sjl_xattr_write_field FILE FIELD_NAME VALUE
# Writes a single SJL field to all applicable xattr namespaces.
sjl_xattr_write_field() {
    local file="$1" field="$2" value="$3"
    [[ ! -f "$file" ]] && return 1
    [[ -z "$value" || "$value" == "null" ]] && return 0

    # Always write to the SJL private namespace (works on both platforms)
    local sjl_key="com.shannonjlove.sjl.${field}"
    _sjl_xattr_set "$file" "$sjl_key" "$value"

    # Linux: also write as user.sjl.* (POSIX standard, filesystem-agnostic)
    if sjl_is_linux; then
        _sjl_xattr_set "$file" "user.sjl.${field}" "$value"
        return 0
    fi

    # macOS: write to kMDItem namespace for Spotlight-indexed fields
    case "$field" in
        SJLauthors)           _sjl_xattr_set "$file" "com.apple.metadata:kMDItemAuthors"                "$value" ;;
        SJLcopyright)         _sjl_xattr_set "$file" "com.apple.metadata:kMDItemCopyright"              "$value" ;;
        SJLdescription)       _sjl_xattr_set "$file" "com.apple.metadata:kMDItemDescription"            "$value" ;;
        SJLkeywords)          _sjl_xattr_set "$file" "com.apple.metadata:kMDItemKeywords"               "$value" ;;
        SJLlanguages)         _sjl_xattr_set "$file" "com.apple.metadata:kMDItemLanguages"              "$value" ;;
        SJLlatitude|SJLgpsLatitude)
                              _sjl_xattr_set "$file" "com.apple.metadata:kMDItemLatitude"               "$value" ;;
        SJLlongitude|SJLgpsLongitude)
                              _sjl_xattr_set "$file" "com.apple.metadata:kMDItemLongitude"              "$value" ;;
        SJLaltitude|SJLgpsAltitude)
                              _sjl_xattr_set "$file" "com.apple.metadata:kMDItemAltitude"               "$value" ;;
        SJLdurationSeconds)   _sjl_xattr_set "$file" "com.apple.metadata:kMDItemDurationSeconds"        "$value" ;;
        SJLaperture)          _sjl_xattr_set "$file" "com.apple.metadata:kMDItemApertureSize"           "$value" ;;
        SJLiso|SJLisoSpeed)   _sjl_xattr_set "$file" "com.apple.metadata:kMDItemISOSpeed"               "$value" ;;
        SJLfocalLength)       _sjl_xattr_set "$file" "com.apple.metadata:kMDItemFocalLength"            "$value" ;;
        SJLfocalLength35mm)   _sjl_xattr_set "$file" "com.apple.metadata:kMDItemFocalLength35mm"        "$value" ;;
        SJLcameraMake|SJLdeviceMake)
                              _sjl_xattr_set "$file" "com.apple.metadata:kMDItemAcquisitionMake"        "$value" ;;
        SJLcameraModel|SJLdeviceModel)
                              _sjl_xattr_set "$file" "com.apple.metadata:kMDItemAcquisitionModel"       "$value" ;;
        SJLpixelWidth|SJLimageWidth)
                              _sjl_xattr_set "$file" "com.apple.metadata:kMDItemPixelWidth"             "$value" ;;
        SJLpixelHeight|SJLimageHeight)
                              _sjl_xattr_set "$file" "com.apple.metadata:kMDItemPixelHeight"            "$value" ;;
        SJLpixelCount)        _sjl_xattr_set "$file" "com.apple.metadata:kMDItemPixelCount"             "$value" ;;
        SJLresolutionWidth)   _sjl_xattr_set "$file" "com.apple.metadata:kMDItemResolutionWidthDPI"     "$value" ;;
        SJLresolutionHeight)  _sjl_xattr_set "$file" "com.apple.metadata:kMDItemResolutionHeightDPI"    "$value" ;;
        SJLbitDepth)          _sjl_xattr_set "$file" "com.apple.metadata:kMDItemBitsPerSample"          "$value" ;;
        SJLcolorSpace)        _sjl_xattr_set "$file" "com.apple.metadata:kMDItemColorSpace"             "$value" ;;
        SJLvideoFrameRate)    _sjl_xattr_set "$file" "com.apple.metadata:kMDItemVideoFrameRate"         "$value" ;;
        SJLaudioBitRate)      _sjl_xattr_set "$file" "com.apple.metadata:kMDItemAudioBitRate"           "$value" ;;
        SJLaudioSampleRate)   _sjl_xattr_set "$file" "com.apple.metadata:kMDItemAudioSampleRate"        "$value" ;;
        SJLbeatsPerMinute)    _sjl_xattr_set "$file" "com.apple.metadata:kMDItemBeatsPerMinute"         "$value" ;;
        SJLmusicalGenre|SJLgenre)
                              _sjl_xattr_set "$file" "com.apple.metadata:kMDItemMusicalGenre"           "$value" ;;
        SJLrecordingDate)     _sjl_xattr_set "$file" "com.apple.metadata:kMDItemRecordingDate"          "$value" ;;
        SJLcreatedDate)       _sjl_xattr_set "$file" "com.apple.metadata:kMDItemContentCreationDate"    "$value" ;;
        SJLmodifiedDate)      _sjl_xattr_set "$file" "com.apple.metadata:kMDItemContentModificationDate" "$value" ;;
        SJLpages)             _sjl_xattr_set "$file" "com.apple.metadata:kMDItemNumberOfPages"          "$value" ;;
        SJLpageWidth)         _sjl_xattr_set "$file" "com.apple.metadata:kMDItemPageWidth"              "$value" ;;
        SJLpageHeight)        _sjl_xattr_set "$file" "com.apple.metadata:kMDItemPageHeight"             "$value" ;;
        SJLcontributors)      _sjl_xattr_set "$file" "com.apple.metadata:kMDItemContributors"           "$value" ;;
        SJLcoverage)          _sjl_xattr_set "$file" "com.apple.metadata:kMDItemCoverage"               "$value" ;;
        SJLrating)            _sjl_xattr_set "$file" "com.apple.metadata:kMDItemStarRating"             "$value" ;;
        SJLrights)            _sjl_xattr_set "$file" "com.apple.metadata:kMDItemRights"                 "$value" ;;
        SJLpublishers)        _sjl_xattr_set "$file" "com.apple.metadata:kMDItemPublishers"             "$value" ;;
        SJLsubject)           _sjl_xattr_set "$file" "com.apple.metadata:kMDItemSubject"                "$value" ;;
        SJLheadline|SJLsemanticTitle)
                              _sjl_xattr_set "$file" "com.apple.metadata:kMDItemHeadline"               "$value" ;;
        SJLcomment)           _sjl_xattr_set "$file" "com.apple.metadata:kMDItemComment"                "$value" ;;
        SJLspotlightComment)  _sjl_xattr_set "$file" "com.apple.metadata:kMDItemFinderComment"          "$value" ;;
        SJLlocation|SJLaddress)
                              _sjl_xattr_set "$file" "com.apple.metadata:kMDItemCity"                   "$value" ;;
        SJLcity|SJLiptcCity)  _sjl_xattr_set "$file" "com.apple.metadata:kMDItemCity"                   "$value" ;;
        SJLstate|SJLiptcProvinceState)
                              _sjl_xattr_set "$file" "com.apple.metadata:kMDItemStateOrProvince"        "$value" ;;
        SJLcountry|SJLiptcCountry)
                              _sjl_xattr_set "$file" "com.apple.metadata:kMDItemCountry"                "$value" ;;
        SJLfNumber)           _sjl_xattr_set "$file" "com.apple.metadata:kMDItemFNumber"                "$value" ;;
        SJLexposureProgram)   _sjl_xattr_set "$file" "com.apple.metadata:kMDItemExposureProgram"        "$value" ;;
        SJLexposureTime)      _sjl_xattr_set "$file" "com.apple.metadata:kMDItemExposureTimeSeconds"    "$value" ;;
        SJLwhiteBalance)      _sjl_xattr_set "$file" "com.apple.metadata:kMDItemWhiteBalance"           "$value" ;;
        SJLflash)             _sjl_xattr_set "$file" "com.apple.metadata:kMDItemFlashOnOff"             "$value" ;;
        SJLspotlightWhereFroms)
                              _sjl_xattr_set "$file" "com.apple.metadata:kMDItemWhereFroms"             "$value" ;;
        SJLtvEpisodeTitle)    _sjl_xattr_set "$file" "com.apple.metadata:kMDItemTVEpisodeTitle"         "$value" ;;
        SJLtvShow)            _sjl_xattr_set "$file" "com.apple.metadata:kMDItemTVShow"                 "$value" ;;
        SJLtvSeason)          _sjl_xattr_set "$file" "com.apple.metadata:kMDItemTVSeason"               "$value" ;;
        SJLtvEpisode)         _sjl_xattr_set "$file" "com.apple.metadata:kMDItemTVEpisodeID"            "$value" ;;
        SJLtvNetwork)         _sjl_xattr_set "$file" "com.apple.metadata:kMDItemTVNetwork"              "$value" ;;
        SJLencod|SJLencodingSoftware)
                              _sjl_xattr_set "$file" "com.apple.metadata:kMDItemEncodingApplications"   "$value" ;;
        SJLparticipants)      _sjl_xattr_set "$file" "com.apple.metadata:kMDItemParticipants"           "$value" ;;
        SJLeditors)           _sjl_xattr_set "$file" "com.apple.metadata:kMDItemEditors"                "$value" ;;
        SJLmedioTypes|SJLmediaTypes)
                              _sjl_xattr_set "$file" "com.apple.metadata:kMDItemMediaTypes"             "$value" ;;
        SJLalbum)             _sjl_xattr_set "$file" "com.apple.metadata:kMDItemAlbum"                  "$value" ;;
        SJLcomposer)          _sjl_xattr_set "$file" "com.apple.metadata:kMDItemComposer"               "$value" ;;
        SJLlyricist)          _sjl_xattr_set "$file" "com.apple.metadata:kMDItemLyricist"               "$value" ;;
        SJLperformers)        _sjl_xattr_set "$file" "com.apple.metadata:kMDItemPerformers"             "$value" ;;
        SJLorganizations)     _sjl_xattr_set "$file" "com.apple.metadata:kMDItemOrganizations"          "$value" ;;
        SJLnamedPeople)       _sjl_xattr_set "$file" "com.apple.metadata:kMDItemNamedPeople"            "$value" ;;
        SJLcontentCreator)    _sjl_xattr_set "$file" "com.apple.metadata:kMDItemCreator"                "$value" ;;
        SJLdirector)          _sjl_xattr_set "$file" "com.apple.metadata:kMDItemDirector"               "$value" ;;
        SJLproducer)          _sjl_xattr_set "$file" "com.apple.metadata:kMDItemProducer"               "$value" ;;
        SJLstudio)            _sjl_xattr_set "$file" "com.apple.metadata:kMDItemStudio"                 "$value" ;;
        SJLlens|SJLlensModel) _sjl_xattr_set "$file" "com.apple.metadata:kMDItemLensModel"              "$value" ;;
        SJLspotlightCodecs)   _sjl_xattr_set "$file" "com.apple.metadata:kMDItemCodecs"                 "$value" ;;
        SJLcompressorName)    _sjl_xattr_set "$file" "com.apple.metadata:kMDItemVideoEncodingApplications" "$value" ;;
        SJLinstructions)      _sjl_xattr_set "$file" "com.apple.metadata:kMDItemInstruction"            "$value" ;;
        SJLsecurity)          _sjl_xattr_set "$file" "com.apple.metadata:kMDItemSecurityMethod"         "$value" ;;
        SJLfonts)             _sjl_xattr_set "$file" "com.apple.metadata:kMDItemFonts"                  "$value" ;;
        SJLidentifier)        _sjl_xattr_set "$file" "com.apple.metadata:kMDItemIdentifier"             "$value" ;;
        SJLorientation)       _sjl_xattr_set "$file" "com.apple.metadata:kMDItemOrientation"            "$value" ;;
        SJLdurationMMSS|SJLdurationHHMMSS)
                              _sjl_xattr_set "$file" "com.apple.metadata:kMDItemDurationSeconds"        "$value" ;;
        # All other SJL-specific fields: private namespace only (already written above)
        *) : ;;
    esac
}

# =============================================================================
# BULK CORE FIELDS WRITE
# =============================================================================

# sjl_xattr_write_core FILE UUID24 PARA CLOUD PROJECT PROCESSED
# Writes the six most critical SJL identity fields in one call.
sjl_xattr_write_core() {
    local file="$1" uuid24="$2" para="$3" cloud="$4" project="$5" processed="$6"
    sjl_xattr_write_field "$file" SJLuuid24      "$uuid24"
    sjl_xattr_write_field "$file" SJLparabucket  "$para"
    sjl_xattr_write_field "$file" SJLcloud        "$cloud"
    sjl_xattr_write_field "$file" SJLproject      "$project"
    sjl_xattr_write_field "$file" SJLprocessed    "$processed"
    sjl_xattr_write_field "$file" SJLidentifier   "$uuid24"
}

# sjl_xattr_write_location FILE ADDRESS CITY STATE COUNTRY LAT LON
sjl_xattr_write_location() {
    local file="$1" address="$2" city="$3" state="$4" country="$5" lat="$6" lon="$7"
    sjl_xattr_write_field "$file" SJLaddress   "$address"
    sjl_xattr_write_field "$file" SJLcity      "$city"
    sjl_xattr_write_field "$file" SJLstate     "$state"
    sjl_xattr_write_field "$file" SJLcountry   "$country"
    sjl_xattr_write_field "$file" SJLlatitude  "$lat"
    sjl_xattr_write_field "$file" SJLlongitude "$lon"
    sjl_xattr_write_field "$file" SJLgpsLatitude  "$lat"
    sjl_xattr_write_field "$file" SJLgpsLongitude "$lon"
    # Combined location string for Spotlight search
    local loc_str="$city, $state, $country"
    sjl_xattr_write_field "$file" SJLlocation  "$loc_str"
    sjl_xattr_write_field "$file" SJLiptcCity  "$city"
    sjl_xattr_write_field "$file" SJLiptcCountry "$country"
    sjl_xattr_write_field "$file" SJLiptcProvinceState "$state"
}

# sjl_xattr_write_links FILE HOOKMARK UNIVERSAL RAINDROP HUB
sjl_xattr_write_links() {
    local file="$1" hookmark="$2" universal="$3" raindrop_id="$4" hub="$5"
    sjl_xattr_write_field "$file" SJLhookmarkURL  "$hookmark"
    sjl_xattr_write_field "$file" SJLuniversalURL "$universal"
    sjl_xattr_write_field "$file" SJLraindropID   "$raindrop_id"
    sjl_xattr_write_field "$file" SJLhubLink      "$hub"
    sjl_xattr_write_field "$file" SJLsearchLink   "hook://search?q=${universal##*=}"
}

# sjl_xattr_write_craft FILE DOCID PARA_CODE PARA_ROOT SEMANTIC_TITLE VERSION_MAJOR VERSION_MINOR SHA8 SENSITIVITY
sjl_xattr_write_craft() {
    local file="$1" docid="$2" paracode="$3" pararoot="$4" title="$5"
    local vmajor="$6" vminor="$7" sha8="$8" sensitivity="${9:-internal}"
    sjl_xattr_write_field "$file" SJLdocid          "$docid"
    sjl_xattr_write_field "$file" SJLparacode        "$paracode"
    sjl_xattr_write_field "$file" SJLpararoot        "$pararoot"
    sjl_xattr_write_field "$file" SJLsemanticTitle   "$title"
    sjl_xattr_write_field "$file" SJLversionMajor    "$vmajor"
    sjl_xattr_write_field "$file" SJLversionMinor    "$vminor"
    sjl_xattr_write_field "$file" SJLsha8            "$sha8"
    sjl_xattr_write_field "$file" SJLsensitivity     "$sensitivity"
    sjl_xattr_write_field "$file" SJLheadline        "$title"
}

# sjl_xattr_write_camera FILE MAKE MODEL ISO APERTURE SHUTTER FOCAL_LENGTH
sjl_xattr_write_camera() {
    local file="$1" make="$2" model="$3" iso="$4" aperture="$5" shutter="$6" focal="$7"
    sjl_xattr_write_field "$file" SJLcameraMake    "$make"
    sjl_xattr_write_field "$file" SJLcameraModel   "$model"
    sjl_xattr_write_field "$file" SJLdeviceMake    "$make"
    sjl_xattr_write_field "$file" SJLdeviceModel   "$model"
    sjl_xattr_write_field "$file" SJLiso           "$iso"
    sjl_xattr_write_field "$file" SJLisoSpeed      "$iso"
    sjl_xattr_write_field "$file" SJLaperture      "$aperture"
    sjl_xattr_write_field "$file" SJLshutterSpeed  "$shutter"
    sjl_xattr_write_field "$file" SJLfocalLength   "$focal"
    sjl_xattr_write_field "$file" SJLshotOn        "$make $model"
}

# sjl_xattr_write_tagbot FILE DESC TAGS MODEL SCORE CAPTION OBJECTS
sjl_xattr_write_tagbot() {
    local file="$1" desc="$2" tags="$3" model="$4" score="$5" caption="$6" objects="$7"
    sjl_xattr_write_field "$file" SJLtagbotDesc    "$desc"
    sjl_xattr_write_field "$file" SJLtagbotTags    "$tags"
    sjl_xattr_write_field "$file" SJLtagbotModel   "$model"
    sjl_xattr_write_field "$file" SJLtagbotScore   "$score"
    sjl_xattr_write_field "$file" SJLtagbotCaption "$caption"
    sjl_xattr_write_field "$file" SJLtagbotObjects "$objects"
    sjl_xattr_write_field "$file" SJLtagbotRunAt   "$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
    # Mirror caption to Spotlight description
    [[ -n "$caption" ]] && sjl_xattr_write_field "$file" SJLdescription "$caption"
    [[ -n "$tags" ]]    && sjl_xattr_write_field "$file" SJLkeywords    "$tags"
}

# =============================================================================
# READ FUNCTIONS
# =============================================================================

# sjl_xattr_read FILE FIELD_NAME
# Returns the value of a SJL xattr field (private namespace).
sjl_xattr_read() {
    local file="$1" field="$2"
    local key="com.shannonjlove.sjl.${field}"
    if sjl_is_mac; then
        xattr -p "$key" "$file" 2>/dev/null || true
    else
        getfattr -n "user.sjl.${field}" --only-values "$file" 2>/dev/null || true
    fi
}

# sjl_xattr_read_all FILE
# Dumps all SJL xattrs for the file as KEY=VALUE lines.
sjl_xattr_read_all() {
    local file="$1"
    if sjl_is_mac; then
        xattr -l "$file" 2>/dev/null | grep -E 'com\.shannonjlove\.sjl\.' || true
    else
        getfattr -d -m "user\.sjl\." "$file" 2>/dev/null || true
    fi
}

# =============================================================================
# JSON SIDECAR — CLOUD-RESILIENT FALLBACK
# =============================================================================
# Sidecar filename: <original-file>.sjl.json
# This file travels with the original and is readable by any tool.
# It is the authoritative metadata record when XMP/xattrs are stripped.

# sjl_sidecar_path FILE
# Returns the path to the sidecar for FILE.
sjl_sidecar_path() {
    echo "${1}.sjl.json"
}

# sjl_sidecar_write FILE JSON_STRING
# Writes a complete JSON string to the sidecar file.
sjl_sidecar_write() {
    local file="$1" json="$2"
    local sidecar="${file}.sjl.json"
    printf '%s\n' "$json" > "$sidecar"
}

# sjl_sidecar_from_exif FILE
# Reads all XMP-SJL fields from the file via ExifTool and writes them
# to the JSON sidecar. Requires ExifTool with sjl.ExifTool_config installed.
sjl_sidecar_from_exif() {
    local file="$1"
    [[ ! -f "$file" ]] && return 1
    local sidecar="${file}.sjl.json"

    python3 - "$file" "$sidecar" <<'PYEOF'
import sys, json, subprocess, re

file_path  = sys.argv[1]
sidecar    = sys.argv[2]

try:
    result = subprocess.run(
        ["exiftool", "-j", "-XMP-SJL:all", file_path],
        capture_output=True, text=True, timeout=30
    )
    if result.returncode != 0 or not result.stdout.strip():
        sys.exit(0)
    data = json.loads(result.stdout)
    if not data:
        sys.exit(0)
    raw = data[0]
    # Keep only SJL-prefixed keys; strip ExifTool group prefix if present
    sjl = {}
    for k, v in raw.items():
        clean_k = re.sub(r'^.*:', '', k)  # remove "XMP-SJL:" prefix
        if clean_k.startswith('SJL'):
            sjl[clean_k] = v
    if sjl:
        sjl["schema_version"] = "1.0"
        sjl["source_file"]    = file_path
        with open(sidecar, 'w') as f:
            json.dump(sjl, f, indent=2, ensure_ascii=False)
        print(f"Sidecar written: {sidecar}")
except Exception as e:
    print(f"WARN: sidecar_from_exif failed: {e}", file=sys.stderr)
PYEOF
}

# sjl_sidecar_read FILE FIELD_NAME
# Reads a single field from the JSON sidecar. Returns empty string if not found.
sjl_sidecar_read() {
    local file="$1" field="$2"
    local sidecar="${file}.sjl.json"
    [[ ! -f "$sidecar" ]] && return 0
    python3 -c "
import json, sys
try:
    d = json.load(open('$sidecar'))
    print(d.get('$field', ''), end='')
except: pass
" 2>/dev/null || true
}

# sjl_sidecar_build_json FILE UUID24 PARA CLOUD PROJECT PROCESSED [extra key=val ...]
# Builds and writes a minimal SJL JSON sidecar. Additional key=val pairs
# can be passed as trailing arguments.
sjl_sidecar_build_json() {
    local file="$1" uuid24="$2" para="$3" cloud="$4" project="$5" processed="$6"
    shift 6

    # Start with mandatory fields
    local json
    json=$(python3 - <<PYEOF
import json, sys, os
d = {
    "schema_version": "1.0",
    "SJLuuid24":     "$uuid24",
    "SJLparabucket": "$para",
    "SJLcloud":      "$cloud",
    "SJLproject":    "$project",
    "SJLprocessed":  "$processed",
    "source_file":   "$file",
    "original_filename": os.path.basename("$file"),
}
# Parse extra key=val arguments
extras = sys.argv[1:]
for arg in extras:
    if '=' in arg:
        k, v = arg.split('=', 1)
        d[k.strip()] = v.strip()
print(json.dumps(d, indent=2, ensure_ascii=False))
PYEOF
    )

    # Append any extra args
    if [[ $# -gt 0 ]]; then
        json=$(python3 - <<PYEOF
import json, sys
d = json.loads(sys.stdin.read())
for arg in sys.argv[1:]:
    if '=' in arg:
        k, v = arg.split('=', 1)
        d[k.strip()] = v.strip()
print(json.dumps(d, indent=2, ensure_ascii=False))
PYEOF
        <<< "$json" "$@")
    fi

    sjl_sidecar_write "$file" "$json"
}

# =============================================================================
# FULL WRITE — ALL THREE LAYERS IN ONE CALL
# =============================================================================
# sjl_persist_all FILE UUID24 PARA CLOUD PROJECT PROCESSED
# Writes: (1) XMP via ExifTool, (2) all xattrs, (3) JSON sidecar.
# Requires ExifTool with config installed.
sjl_persist_all() {
    local file="$1" uuid24="$2" para="$3" cloud="$4" project="$5"
    local processed="${6:-$(date -u '+%Y-%m-%dT%H:%M:%SZ')}"

    # Layer 1: XMP embedded metadata
    if command -v exiftool &>/dev/null; then
        exiftool -overwrite_original -q \
            "-XMP-xmp:Identifier=$uuid24" \
            "-XMP-SJL:SJLuuid24=$uuid24" \
            "-XMP-SJL:SJLparabucket=$para" \
            "-XMP-SJL:SJLcloud=$cloud" \
            "-XMP-SJL:SJLproject=$project" \
            "-XMP-SJL:SJLprocessed=$processed" \
            "$file" 2>/dev/null || true

        # Layer 3: JSON sidecar built from ExifTool output (catches all fields)
        sjl_sidecar_from_exif "$file"
    fi

    # Layer 2: xattrs
    sjl_xattr_write_core "$file" "$uuid24" "$para" "$cloud" "$project" "$processed"

    # Minimal sidecar if ExifTool was unavailable
    local sidecar="${file}.sjl.json"
    [[ ! -f "$sidecar" ]] && sjl_sidecar_build_json \
        "$file" "$uuid24" "$para" "$cloud" "$project" "$processed"
}

# =============================================================================
# CLOUD PERSISTENCE NOTES
# =============================================================================
# Cloud service    XMP preserved?  xattrs preserved?  Sidecar preserved?
# ─────────────    ──────────────  ─────────────────  ──────────────────
# Google Drive     YES             NO                 YES (as separate file)
# Dropbox          YES             NO                 YES
# pCloud           YES             NO                 YES
# MEGA             YES             NO                 YES
# iCloud Drive     YES             PARTIAL*           YES
# MediaFire        PARTIAL**       NO                 YES
# Any social/CDN   NO              NO                 N/A (links, not files)
#
# * iCloud preserves xattrs via AppleDouble (._ sidecar) on non-HFS volumes
# ** MediaFire recompresses images; XMP may be stripped; sidecar essential
#
# RECOMMENDATION: always write all three layers on every file.
# =============================================================================
