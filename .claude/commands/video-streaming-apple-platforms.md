# Video Streaming: Apple Platforms (iOS, tvOS, macOS)

Proper streaming architecture for Jellyfin and self-hosted media to Apple devices.

## Protocol Support by Platform

| Protocol | iOS | tvOS | macOS | Notes |
|---|---|---|---|---|
| HLS (.m3u8) | Native, hardware-accelerated | Native, hardware-accelerated | Native | Apple's own protocol; always prefer |
| HTTP range requests (206) | Via AVKit / Infuse | Via AVKit / Infuse | Via AVKit / IINA / Infuse | Works for direct-play with faststart MP4 |
| AirPlay 2 | Cast source | Receiver | Cast source + receiver | Apple local network casting |
| MPEG-DASH | App-dependent only | App-dependent only | App-dependent only | Avoid for Apple targets |

## Server-Side Prerequisites

### MOOV Atom (MP4 faststart)

MP4 files have a metadata section (MOOV atom) written at the end by default. Players must download the entire file before playback unless it's moved to the front.

```bash
# Fix single file (no re-encode)
ffmpeg -i input.mp4 -movflags faststart -c copy output.mp4

# Batch fix entire library
find /mnt/nas/media -name "*.mp4" | while read f; do
  ffmpeg -i "$f" -movflags faststart -c copy "${f%.mp4}_tmp.mp4" && mv "${f%.mp4}_tmp.mp4" "$f"
done
```

### HLS Generation with ffmpeg

Pre-generating HLS is optional with Jellyfin (it transcodes on-the-fly), but needed for direct S3/CDN delivery.

```bash
# Single bitrate (copy streams, no re-encode)
ffmpeg -i input.mp4 \
  -codec: copy \
  -hls_time 6 \
  -hls_list_size 0 \
  -hls_segment_filename 'seg%03d.ts' \
  -f hls output.m3u8

# Adaptive bitrate (ABR) — re-encodes
ffmpeg -i input.mp4 \
  -map 0:v -map 0:a -map 0:v -map 0:a \
  -c:v:0 h264 -b:v:0 5000k \
  -c:v:1 h264 -b:v:1 2000k \
  -c:a aac -b:a 128k \
  -var_stream_map "v:0,a:0 v:1,a:1" \
  -master_pl_name master.m3u8 \
  -hls_time 6 -hls_list_size 0 \
  -hls_segment_filename 'v%v/seg%03d.ts' \
  -f hls v%v/stream.m3u8
```

## Jellyfin: Core Server for All Apple Clients

Jellyfin is the media server. Configure once; all clients benefit.

**Direct Play Priority Order** (Jellyfin attempts in this order):
1. **Direct play** — client plays file as-is (zero CPU, best quality)
2. **Direct stream** — server remuxes container only (minimal load)
3. **Transcode** — full re-encode to HLS for codec/container compatibility

**Key Jellyfin settings** (Dashboard → Playback):
- Enable Hardware Acceleration (VAAPI on Linux)
- Enable Direct Play and Direct Stream
- Enable Dolby Atmos passthrough for Apple TV 4K
- Set Transcode Path to a fast local disk, not NAS

## iOS Streaming

### AVKit — The Correct Framework

Use `AVPlayerViewController` (the full AVKit layer), not raw `AVPlayer` directly. AVKit provides the complete native playback UI, Picture in Picture, AirPlay route picker, and proper HLS handling automatically.

```swift
import AVKit

func play(url: URL) {
    let player = AVPlayer(url: url)
    let controller = AVPlayerViewController()
    controller.player = player
    controller.allowsPictureInPicturePlayback = true  // iOS 14+
    present(controller, animated: true) {
        player.play()
    }
}
```

**Jellyfin stream URLs:**

```swift
// HLS (transcoded — universal compatibility)
let hlsURL = URL(string:
    "https://jellyfin.yourdomain.com/Videos/\(itemId)/master.m3u8?api_key=\(token)&VideoCodec=h264&AudioCodec=aac"
)!

// Direct play (faststart MP4 — zero transcoding)
let directURL = URL(string:
    "https://jellyfin.yourdomain.com/Videos/\(itemId)/stream.mp4?Static=true&api_key=\(token)"
)!
```

### SwiftUI VideoPlayer

```swift
import AVKit

struct VideoView: View {
    let url: URL
    var body: some View {
        VideoPlayer(player: AVPlayer(url: url))
    }
}
```

### Recommended iOS Clients for Jellyfin

| App | Cost | Direct Play | HLS | Offline | Notes |
|---|---|---|---|---|---|
| **Infuse 7** (Firecore) | Free / Pro $9.99/yr | Yes | Yes | Pro only | Best overall; connects natively to Jellyfin; widest codec support |
| **Jellyfin iOS** (official) | Free | Yes | Yes | No | Official, actively developed |
| **Swiftfin** | Free (OSS) | Yes | Yes | No | Community SwiftUI client |
| **VLC for iOS** | Free | Yes | Yes | No | Universal fallback |

**Infuse** is the preferred client — direct plays virtually all codecs without triggering Jellyfin transcoding, and supports offline downloads with Pro.

## tvOS Streaming

### AVKit on tvOS

Same `AVPlayerViewController` API as iOS. tvOS adds focus-engine navigation; AVKit handles it automatically.

```swift
import AVKit

func play(url: URL) {
    let player = AVPlayer(url: url)
    let controller = AVPlayerViewController()
    controller.player = player
    present(controller, animated: true) { player.play() }
}
```

**tvOS-specific considerations:**
- No offline downloads — all streaming must be live
- AirPlay 2 receiver built in; any Apple device can cast to Apple TV
- Apple TV 4K supports Dolby Vision, HDR10, Dolby Atmos — enable passthrough in Jellyfin
- Siri Remote swipe gestures for scrubbing are handled by AVKit automatically
- `AVPlayerViewController` shows the standard tvOS transport bar automatically

### Top Shelf Extension (tvOS)

Surface recently watched or recommended content from Jellyfin directly on the Apple TV home screen by implementing `TVTopShelfProvider` or `TVTopShelfContentProvider` in your tvOS app.

### Recommended tvOS Clients for Jellyfin

| App | Cost | Notes |
|---|---|---|
| **Infuse 7** | Free / Pro | Best tvOS experience; Dolby Vision + Atmos passthrough |
| **Jellyfin for tvOS** (official) | Free | Native layout, official support |
| **Swiftfin (tvOS)** | Free | Community-built SwiftUI |
| **VLC for Apple TV** | Free | Good fallback codec coverage |

## macOS Streaming

### AVKit on macOS

```swift
// SwiftUI
import AVKit
struct VideoView: View {
    var body: some View {
        VideoPlayer(player: AVPlayer(url: streamURL))
            .frame(minWidth: 640, minHeight: 360)
    }
}

// AppKit
import AVKit
let playerView = AVPlayerView()
playerView.player = AVPlayer(url: streamURL)
playerView.player?.play()
```

### Recommended macOS Clients for Jellyfin

| App | Cost | Notes |
|---|---|---|
| **Infuse 7** | Free / Pro | Best direct-play; native macOS design |
| **IINA** | Free | macOS-native, built on mpv; excellent HLS + hardware decode |
| **Jellyfin Media Player** (official) | Free | Electron-based desktop app |
| **Swiftfin (macOS)** | Free | Native SwiftUI macOS client |
| **VLC** | Free | Best codec coverage; universal fallback |
| **Jellyfin Web** | Free | Safari/Chrome at `https://jellyfin.yourdomain.com` |

**IINA** is the top native macOS player for local/streamed content — hardware-accelerated, AirPlay support, integrates with macOS media keys and Now Playing widget.

## AirPlay 2

AirPlay is built into `AVPlayerViewController` / `AVPlayerView` automatically — the route picker appears in the transport controls. For custom UI:

```swift
import AVKit
let routePicker = AVRoutePickerView()
view.addSubview(routePicker)
```

Jellyfin's HLS streams are fully AirPlay-compatible. Jellyfin also has optional DLNA support (enable in Settings → DLNA) for non-AirPlay local network casting.

## S3 + CloudFront for Custom Apps

```bash
# Upload HLS to S3 with correct MIME types
aws s3 sync ./hls/ s3://your-bucket/videos/title/ \
  --include "*.m3u8" --content-type "application/x-mpegURL"
aws s3 sync ./hls/ s3://your-bucket/videos/title/ \
  --include "*.ts"   --content-type "video/MP2T"
```

CloudFront in front of S3 adds edge caching for .ts segments, signed URLs for access control, and HTTPS enforcement (required by iOS App Transport Security).

Deliver to any Apple client: `https://d1234.cloudfront.net/videos/title/master.m3u8`

For production scale use **AWS Elemental MediaConvert** for automated MP4 → HLS conversion (Dashboard → Jobs → create job with HLS output group, 6–10s segments, S3 output).

## Sonarr/Radarr Post-Processing (Automate faststart)

**Settings → Connect → Custom Script** in Sonarr or Radarr:

```bash
#!/usr/bin/env bash
# /home/user/arr-suite/scripts/faststart.sh
FILE="${radarr_moviefile_path:-$sonarr_episodefile_path}"
[[ "$FILE" == *.mp4 ]] || exit 0
TMP="${FILE%.mp4}_tmp.mp4"
ffmpeg -i "$FILE" -movflags faststart -c copy "$TMP" && mv "$TMP" "$FILE"
```

## Decision Matrix

| Use Case | Recommended Approach |
|---|---|
| iOS custom app | `AVPlayerViewController` + Jellyfin HLS or direct-play URL |
| tvOS custom app | `AVPlayerViewController` + Jellyfin HLS + Dolby passthrough |
| macOS custom app | `VideoPlayer` (SwiftUI) or `AVPlayerView` (AppKit) |
| iOS consumer | Infuse → Jellyfin (best), or Jellyfin iOS app |
| Apple TV consumer | Infuse tvOS → Jellyfin (best), or Jellyfin tvOS app |
| Mac consumer | IINA or Infuse macOS → Jellyfin |
| Browser (any OS) | Jellyfin Web UI — faststart MP4 direct plays instantly |
| Casting | AirPlay 2 — automatic in AVKit, or DLNA for non-Apple devices |

## Quick Reference

```bash
# Fix MOOV atom (faststart) — required for streaming
ffmpeg -i in.mp4 -movflags faststart -c copy out.mp4

# Generate HLS
ffmpeg -i in.mp4 -codec: copy -hls_time 6 -hls_list_size 0 -f hls out.m3u8

# Verify server supports range requests
curl -I https://jellyfin.yourdomain.com/Videos/{id}/stream.mp4?Static=true | grep Accept-Ranges
# Expected: Accept-Ranges: bytes
```

## Sources

- Apple AVKit documentation — developer.apple.com/avkit
- Jellyfin documentation — jellyfin.org/docs
- Infuse by Firecore — firecore.com/infuse
- IINA — iina.io
- ffmpeg HLS muxer and movflags docs
