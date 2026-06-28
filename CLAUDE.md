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

### Video Streaming: Apple Platform Strategy (Synthesized)

#### The MOOV Atom (Server-Side Prerequisite)

MP4 files have a metadata section called the **MOOV atom**. By default most encoders place it at the **end** of the file — players must download the entire file before playback can begin. Move it to the front with ffmpeg (no re-encode):

```bash
ffmpeg -i input.mp4 -movflags faststart -c copy output.mp4
```

Automate via a Sonarr/Radarr post-processing script so every downloaded MP4 is fixed automatically before Jellyfin serves it.

#### HLS: The Universal Apple Protocol

HLS (HTTP Live Streaming, `.m3u8` + `.ts` segments) is Apple's native streaming protocol — hardware-accelerated on all Apple silicon. Use it for all Apple platform clients.

```bash
# Generate HLS from MP4 (copy streams, no re-encode)
ffmpeg -i input.mp4 -codec: copy -hls_time 6 -hls_list_size 0 -f hls output.m3u8
```

Jellyfin transcodes to HLS on-the-fly for any client that needs it — no manual pre-conversion required when using Jellyfin clients.

#### Apple Platform Clients

**iOS:** Use `AVPlayerViewController` (AVKit) — not raw `AVPlayer` — for the full native playback UI with PiP and AirPlay controls built in. Best consumer app: **Infuse** (direct plays virtually all codecs, no transcoding).

**tvOS:** Same `AVPlayerViewController` API. Apple TV 4K supports Dolby Vision, HDR10, and Dolby Atmos passthrough — enable in Jellyfin Dashboard → Playback. Best consumer app: **Infuse tvOS**.

**macOS:** Use `VideoPlayer` (SwiftUI) or `AVPlayerView` (AppKit). Best native app: **IINA** (hardware-accelerated, AirPlay, system media controls). Best Jellyfin client: **Infuse macOS** or **Jellyfin Media Player**.

**AirPlay 2:** Built into `AVPlayerViewController` automatically — route picker appears in transport controls. All Jellyfin HLS streams are AirPlay-compatible.

#### Decision Matrix

| Use Case | Recommended Approach |
|---|---|
| iOS custom app | `AVPlayerViewController` + Jellyfin HLS or direct-play URL |
| tvOS custom app | `AVPlayerViewController` + Dolby passthrough via Jellyfin |
| macOS custom app | `VideoPlayer` (SwiftUI) or `AVPlayerView` (AppKit) |
| iOS consumer | Infuse → Jellyfin |
| Apple TV consumer | Infuse tvOS → Jellyfin |
| Mac consumer | IINA or Infuse macOS → Jellyfin |
| Browser | Jellyfin Web — faststart MP4 direct plays instantly |
| Casting | AirPlay 2 (automatic in AVKit) |

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
- `/video-streaming-apple-platforms` — HLS, AVKit (iOS/tvOS/macOS), Infuse/IINA client guide, ffmpeg faststart/HLS, AirPlay, S3/CloudFront, Sonarr post-processing hook
