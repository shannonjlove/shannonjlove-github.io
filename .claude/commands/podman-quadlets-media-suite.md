# Podman Quadlets Media Suite

Complete self-hosted media automation suite using the Arr stack, Podman Quadlets, and systemd.

## Architecture

```
Prowlarr (indexers) → Sonarr/Radarr/Lidarr/Readarr (managers) → qBittorrent (downloader) → Bazarr (subtitles) → Jellyfin (streaming)
```

All services run in a single Podman network (`arr-suite`) on subnet `10.89.0.0/16`, behind Traefik reverse proxy with automatic Let's Encrypt SSL.

## Service Ports

| Service | Port | Purpose |
|---|---|---|
| Prowlarr | 9696 | Indexer manager (200+ trackers) |
| Sonarr | 8989 | TV show automation |
| Radarr | 7878 | Movie automation |
| Lidarr | 8686 | Music automation |
| Readarr | 8787 | Ebook/audiobook automation |
| qBittorrent | 8080 | Download client |
| Bazarr | 6767 | Subtitle automation |
| Jellyfin | 8096 | Media streaming |
| Audiobookshelf | 13378 | Audiobook/podcast server |
| ConvertX | 3000 | File format converter (1000+ formats) |
| ThinkDashboard | 8082 | Bookmark dashboard |
| Traefik | 80/443 | Reverse proxy + SSL |
| n8n | 5678 | Workflow automation |
| PostgreSQL | 5432 | Database for n8n |
| Jaeger | 16686 | Distributed tracing |
| RustDesk | 21115-21119 | Remote desktop |

## Storage Layout

```
/home/user/arr-suite/config/    # Persistent service configs
/mnt/nas/media/                  # Organized media library
/mnt/nas/downloads/              # Download staging area
```

## Quadlet Configuration Pattern

Each service is a `.container` file in `~/.config/containers/systemd/` (rootless) or `/etc/containers/systemd/` (system):

```ini
[Unit]
Description=<service> container
Wants=network-online.target
After=network-online.target arr-suite-network.service <dependencies>
Requires=arr-suite-network.service <dependencies>

[Container]
Image=lscr.io/linuxserver/<service>:latest
ContainerName=<service>
PublishPort=<port>:<port>
Network=arr-suite.network
Volume=/home/user/arr-suite/config/<service>:/config:z
Volume=/mnt/nas/media:/media:z
Volume=/mnt/nas/downloads:/downloads:z
Environment=PUID=1000
Environment=PGID=1000
Environment=TZ=America/Chicago
Label=io.containers.autoupdate=registry
Label=traefik.enable=true
Label=traefik.http.routers.<service>.rule=Host(`<service>.yourdomain.com`)
Label=traefik.http.routers.<service>.tls=true
Label=traefik.http.routers.<service>.tls.certresolver=letsencrypt
Label=traefik.http.services.<service>.loadbalancer.server.port=<port>
Label=traefik.http.routers.<service>.middlewares=default-headers@file

[Service]
Restart=always

[Install]
WantedBy=default.target
```

## Network Quadlet

```ini
# arr-suite.network
[Network]
Subnet=10.89.0.0/16
Label=app=arr-suite
```

## Key Security Principles

- **Rootless containers**: All services run without root (`PUID`/`PGID` as regular user)
- **SELinux**: Volume mounts use `:z` flag for automatic label relabeling
- **Network isolation**: Services communicate on internal network; only Traefik exposes external ports
- **Automatic SSL**: Let's Encrypt via Traefik `letsencrypt` cert resolver
- **Auto-updates**: `io.containers.autoupdate=registry` label enables `podman auto-update`

## Startup Dependency Order

1. `arr-suite-network.service` (Podman network)
2. `qbittorrent.service` + `prowlarr.service` (download client + indexers)
3. `sonarr.service` + `radarr.service` + `lidarr.service` + `readarr.service` (media managers)
4. `bazarr.service` (subtitles, needs Sonarr/Radarr)
5. `jellyfin.service` (media server, needs organized library)
6. `traefik.service` (can start early, routes to ready services)

## Management Script (setup-quadlets.sh)

Key operations:
```bash
./setup-quadlets.sh setup    # Create systemd symlinks, reload daemon, open firewall ports
./setup-quadlets.sh start    # Start all services in dependency order
./setup-quadlets.sh stop     # Stop all services
./setup-quadlets.sh restart  # Restart all services
./setup-quadlets.sh status   # Show systemd status + ports + descriptions
./setup-quadlets.sh ports    # List all exposed ports
./setup-quadlets.sh urls     # Generate service URLs
./setup-quadlets.sh logs     # View service logs
./setup-quadlets.sh shell    # Access container shell
./setup-quadlets.sh inspect  # Container inspection
```

The script auto-discovers services by scanning `quadlets/` for `.container`/`.network` files and resolves startup order from `Requires`/`After` directives.

## Fedora Server Setup Steps

```bash
# 1. Install Podman and enable lingering for rootless systemd
sudo dnf install -y podman
loginctl enable-linger $USER

# 2. Create directory structure
mkdir -p ~/arr-suite/{config,quadlets}
mkdir -p ~/arr-suite/config/{sonarr,radarr,lidarr,readarr,prowlarr,qbittorrent,bazarr,jellyfin,traefik,n8n,audiobookshelf}

# 3. Copy quadlet files to systemd user path
mkdir -p ~/.config/containers/systemd/
cp ~/arr-suite/quadlets/*.container ~/.config/containers/systemd/
cp ~/arr-suite/quadlets/*.network ~/.config/containers/systemd/

# 4. Reload systemd and start
systemctl --user daemon-reload
systemctl --user start arr-suite-network
systemctl --user start prowlarr qbittorrent
systemctl --user start sonarr radarr lidarr readarr
systemctl --user start bazarr jellyfin traefik

# 5. Enable auto-update
systemctl --user enable --now podman-auto-update.timer
```

## Traefik Static Config (traefik.yml)

```yaml
api:
  dashboard: true
  insecure: false

entryPoints:
  web:
    address: ":80"
    http:
      redirections:
        entryPoint:
          to: websecure
          scheme: https
  websecure:
    address: ":443"

providers:
  docker:
    endpoint: "unix:///run/user/1000/podman/podman.sock"
    exposedByDefault: false
    network: arr-suite
  file:
    directory: /config/dynamic
    watch: true

certificatesResolvers:
  letsencrypt:
    acme:
      email: your@email.com
      storage: /config/acme.json
      httpChallenge:
        entryPoint: web

log:
  level: INFO
```

## Traefik Dynamic Config (dynamic/middlewares.yml)

```yaml
http:
  middlewares:
    default-headers:
      headers:
        frameDeny: true
        browserXssFilter: true
        contentTypeNosniff: true
        forceSTSHeader: true
        stsSeconds: 63072000
        stsIncludeSubdomains: true
        stsPreload: true
```

## Firewall Rules (firewalld)

```bash
# Open Traefik ports
sudo firewall-cmd --permanent --add-port=80/tcp
sudo firewall-cmd --permanent --add-port=443/tcp
# RustDesk
sudo firewall-cmd --permanent --add-port=21115-21119/tcp
sudo firewall-cmd --permanent --add-port=21116/udp
sudo firewall-cmd --reload
```

## Reference

- Source article: "Building a Complete Self-Hosted Media Automation Suite with Podman Quadlets" by Miklós Galicz (Medium, Oct 2025)
- Template repo: https://codeberg.org/blackfyre/arr-suite
- Podman Quadlets docs: https://docs.podman.io/en/latest/markdown/podman-systemd.unit.5.html
