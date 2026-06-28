# CLAUDE.md — SJL Homelab & Project Memory

## Persistent Workflow: Self-Hosted Media Suite + Video Streaming Pipeline

### Core Philosophy

The setup uses **Podman Quadlets** (systemd-native container units) on Fedora Server running rootless containers for the full media automation pipeline. All services share the `arr-suite` Podman network (`10.89.0.0/16`). Reverse proxying and SSL are handled by **Nginx Proxy Manager** (web UI, no labels) rather than Traefik.

### Media Automation Pipeline

```
qBittorrent → Prowlarr → [Sonarr/Radarr/Lidarr/Readarr] → [Bazarr] → ffmpeg (optimize) → Jellyfin → clients
```

**Step-by-step flow:**
1. **Prowlarr** manages indexers (200+ trackers) and pushes results to Arr apps
2. **Sonarr/Radarr/Lidarr/Readarr** automate search, grab, and organize downloads
3. **qBittorrent** handles the actual torrent downloads into `/mnt/nas/downloads/`
4. **Bazarr** fetches subtitles after media is organized
5. **ffmpeg faststart** pre-processes MP4 files so the MOOV atom is at the front (critical for streaming — see below)
6. **Jellyfin** serves the library with on-the-fly HLS transcoding for client compatibility

### Video Streaming: Critical Knowledge (Synthesized)

#### The MOOV Atom Problem

MP4 files have a metadata section called the **MOOV atom**. By default most encoders place it at the **end** of the file. When a player tries to stream this, it must download the entire file before playback can begin.

For streaming, the MOOV atom must be at the **front**. Fix with ffmpeg:

```bash
ffmpeg -i input.mp4 -movflags faststart -acodec copy -vcodec copy output.mp4
```

Run this on all MP4 files after they land in the media library. Can be automated via a Sonarr/Radarr post-processing script or an n8n workflow.

#### AVPlayer / iOS Streaming (Critical Limitation)

**AVPlayer does NOT support HTTP range requests (HTTP 206 Partial Content).** It always downloads the full file before playing, regardless of server support or MOOV atom placement.

For iOS apps using AVPlayer, you **must use HLS** (.m3u8 manifest + .ts segments):

```swift
let asset = AVURLAsset(url: URL(string: "https://your.domain.com/videos/video.m3u8")!)
let item = AVPlayerItem(asset: asset)
let player = AVPlayer(playerItem: item)
```

#### Generating HLS with ffmpeg

```bash
ffmpeg -i input.mp4 \
  -codec: copy \
  -start_number 0 \
  -hls_time 10 \
  -hls_list_size 0 \
  -f hls \
  output.m3u8
```

This produces `output.m3u8` + `output0.ts`, `output1.ts`, ... — upload all to S3 or serve from Jellyfin.

#### Jellyfin + HLS

Jellyfin natively transcodes to HLS on-the-fly for clients that need it. For direct-play (no transcoding), MP4 files with MOOV atom at the front (`faststart`) will start immediately in web browsers and most non-iOS clients.

For iOS clients connecting to Jellyfin, Jellyfin's native HLS transcoding handles this automatically — no manual pre-conversion needed.

#### AWS MediaConvert (for production iOS apps)

For dedicated iOS app development serving video from S3:
1. Use **AWS Elemental MediaConvert** to convert MP4 → HLS
2. Output: `.m3u8` manifest + `.ts` segments → upload to S3
3. Point AVPlayer at the `.m3u8` URL
4. Optionally add **CloudFront** in front of S3 for caching and reduced egress cost

CloudFront is not required for basic HLS playback from S3, but adds value at scale.

#### Decision Matrix

| Client | Protocol | Solution |
|---|---|---|
| Browser | HTTP range requests | MP4 with faststart |
| iOS AVPlayer | HLS only | `.m3u8` via ffmpeg or MediaConvert |
| Jellyfin web client | HTTP range + HLS fallback | faststart MP4 (Jellyfin transcodes if needed) |
| Jellyfin iOS app | HLS (Jellyfin handles) | Let Jellyfin transcode |

### Infrastructure Quick Reference

| Service | Port | Container name |
|---|---|---|
| Nginx Proxy Manager admin | 81 | `nginx-proxy-manager` |
| Prowlarr | 9696 | `prowlarr` |
| Sonarr | 8989 | `sonarr` |
| Radarr | 7878 | `radarr` |
| Lidarr | 8686 | `lidarr` |
| Readarr | 8787 | `readarr` |
| qBittorrent | 8080 | `qbittorrent` |
| Bazarr | 6767 | `bazarr` |
| Jellyfin | 8096 | `jellyfin` |

All containers are on network `arr-suite`. In NPM proxy hosts, use container names as the forward hostname (e.g., `sonarr:8989`).

### Management

```bash
cd ~/arr-suite
./setup-quadlets.sh setup     # first-time: symlinks + firewall
./setup-quadlets.sh start     # start all in dependency order
./setup-quadlets.sh status    # check running state
./setup-quadlets.sh logs <svc>  # stream logs
```

### Storage

```
~/arr-suite/config/          # All container configs (persistent)
~/arr-suite/config/npm/      # NPM data + letsencrypt certs
/mnt/nas/media/              # Organized media library
/mnt/nas/downloads/          # Download staging
```

### Key Conventions

- All containers run rootless (PUID/PGID 1000)
- Volume mounts use `:z` for SELinux relabeling
- `Label=io.containers.autoupdate=registry` on all containers → `podman auto-update` via systemd timer
- NPM handles all SSL (Let's Encrypt) through its web UI — no config files needed
- No Traefik labels anywhere — routing is configured manually in NPM at `http://<host>:81`

### Skills / Commands Available

- `/podman-quadlets-media-suite` — full quadlet config patterns, NPM setup, Fedora setup steps, firewall rules
- `/video-streaming-hls-avplayer` — HLS, AVPlayer limitations, ffmpeg commands, MOOV atom, S3/CloudFront
