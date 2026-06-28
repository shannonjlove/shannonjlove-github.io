# quadlet-media-server

A rootful Podman media server stack managed with [Quadlet](https://docs.podman.io/en/latest/markdown/podman-systemd.unit.5.html) (systemd-native container units). All images are sourced from [hotio.dev](https://hotio.dev).

## Services

| Service | Port | Description |
|---|---|---|
| [Jellyfin](https://jellyfin.org) | `8096` | Media server |
| [Radarr](https://radarr.video) | `7878` | Movie collection manager |
| [Sonarr](https://sonarr.tv) | `8989` | TV series collection manager |
| [Prowlarr](https://prowlarr.com) | `9696` | Indexer manager (routed through ProtonVPN) |
| [qBittorrent](https://www.qbittorrent.org) | `8080` | Torrent client ([VueTorrent](https://github.com/VueTorrent/VueTorrent) UI) |
| [Seerr](https://github.com/Fallenbagel/jellyseerr) | `5055` | Media request & discovery management |
| [Configarr](https://configarr.de) | — | Automated quality profile & custom format sync (timer-based) |

## Repository Structure

```
.
├── configarr/
│   └── config/
│       ├── config.yml          # Configarr configuration (TRaSH-Guides templates)
│       └── secrets.yml         # API keys — keep out of version control!
├── etc/
│   ├── containers/
│   │   └── systemd/            # Quadlet container & network unit files
│   │       ├── *.container
│   │       └── media.network
│   ├── firewalld/
│   │   └── services/           # Firewalld service definitions
│   └── systemd/
│       └── system/
│           └── configarr.timer # Runs Configarr daily at 03:00 UTC
└── prowlarr/
    └── config/
        └── wireguard/
            └── wg0.conf        # ProtonVPN WireGuard config — keep out of version control!
```

## Prerequisites

- Podman (rootful)
- systemd Quadlet support (`podman >= 4.4`)
- `firewall-cmd` (firewalld) for port rules
- A ProtonVPN WireGuard configuration (for Prowlarr)

## Data Layout

All persistent data lives under `/mnt/data/`:

```
/mnt/data/
├── appdata/          # Container config volumes
│   ├── jellyfin/
│   ├── radarr/
│   ├── sonarr/
│   ├── prowlarr/
│   ├── qbittorrent/
│   ├── seerr/
│   └── configarr/
│       ├── config/   # Mount configarr/config/ here
│       └── repos/
└── data/
    ├── media/        # Jellyfin library
    │   ├── movies/
    │   └── tv/
    └── torrents/     # qBittorrent downloads
```

## Installation

### 1. Copy unit files

```bash
# Container & network units (system-wide)
sudo cp etc/containers/systemd/* /etc/containers/systemd/

# Configarr timer
sudo cp etc/systemd/system/configarr.timer /etc/systemd/system/

# Firewalld service definitions
sudo cp etc/firewalld/services/* /etc/firewalld/services/
```

### 2. Create Podman secrets

The containers expect two Podman secrets. **Never commit real credentials to version control.**

**ProtonVPN WireGuard config (for Prowlarr):**
```bash
podman secret create wg0_proton prowlarr/config/wireguard/wg0.conf
```

**Configarr API keys:**

Copy `configarr/config/secrets.yml` to a local file, fill in your values, then:
```bash
podman secret create configarr_secrets configarr/config/secrets.yml
```

`secrets.yml` format:
```yaml
QBITTORRENT_USERNAME: <username>
QBITTORRENT_PASSWORD: <password>
RADARR_API_KEY: <key>
SONARR_API_KEY: <key>
```

### 3. Install VueTorrent (optional)

qBittorrent is configured to serve [VueTorrent](https://github.com/VueTorrent/VueTorrent) from `/usr/local/share/VueTorrent`. Install it there or remove the volume mount from `qbittorrent.container`.

### 4. Reload systemd and start services

```bash
sudo systemctl daemon-reload

# Enable and start all containers
sudo systemctl enable --now jellyfin.service radarr.service sonarr.service \
    prowlarr.service qbittorrent.service seerr.service

# Enable Configarr timer
sudo systemctl enable --now configarr.timer

# Enable firewalld services
sudo firewall-cmd --permanent --add-service=jellyfin
sudo firewall-cmd --permanent --add-service=radarr
sudo firewall-cmd --permanent --add-service=sonarr
sudo firewall-cmd --permanent --add-service=prowlarr
sudo firewall-cmd --permanent --add-service=qbittorrent
sudo firewall-cmd --permanent --add-service=seerr
sudo firewall-cmd --reload
```

## Networking

All containers share the `media` Podman network (`10.89.1.0/24`), allowing them to reach each other by container name (e.g. `http://sonarr:8989`).

Prowlarr additionally has `NET_ADMIN` capability and routes its traffic through the ProtonVPN WireGuard tunnel, while still exposing port `9696` on the LAN via `VPN_EXPOSE_PORTS_ON_LAN`.

## Configarr

[Configarr](https://configarr.de) syncs quality profiles and custom formats from [TRaSH-Guides](https://trash-guides.info) to Radarr and Sonarr using the templates defined in `configarr/config/config.yml`. It runs as a one-shot container triggered by a systemd timer at **03:00 UTC** daily.

**Configured profiles:**

| App | Profile |
|---|---|
| Sonarr | WEB-DL (1080p) + Remux-1080p Anime |
| Radarr | HD Bluray + WEB + [Anime] Remux-1080p |

To run Configarr manually:
```bash
sudo systemctl start configarr.service
```

## Auto-Updates

All containers have `AutoUpdate=registry` set. Enable the Podman auto-update timer to apply image updates automatically:

```bash
sudo systemctl enable --now podman-auto-update.timer
```
