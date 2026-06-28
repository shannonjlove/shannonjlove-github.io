# Podman Quadlets Media Suite

Complete self-hosted media automation suite using the Arr stack, Podman Quadlets, and systemd.

## Architecture

```
Prowlarr (indexers) → Sonarr/Radarr/Lidarr/Readarr (managers) → qBittorrent (downloader) → Bazarr (subtitles) → Jellyfin (streaming)
```

All services run in a single Podman network (`arr-suite`) on subnet `10.89.0.0/16`, behind Nginx Proxy Manager for reverse proxying with Let's Encrypt SSL (configured via web UI).

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
| Nginx Proxy Manager | 80/443/81 | Reverse proxy + SSL + admin UI |
| n8n | 5678 | Workflow automation |
| PostgreSQL | 5432 | Database for n8n |
| Jaeger | 16686 | Distributed tracing |
| RustDesk | 21115-21119 | Remote desktop |

## Storage Layout

```
/home/user/arr-suite/config/         # Persistent service configs
/home/user/arr-suite/config/npm/     # NPM data and SSL certs
/mnt/nas/media/                       # Organized media library
/mnt/nas/downloads/                   # Download staging area
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

[Service]
Restart=always

[Install]
WantedBy=default.target
```

## Nginx Proxy Manager Quadlet

```ini
[Unit]
Description=nginx-proxy-manager container
Wants=network-online.target
After=network-online.target arr-suite-network.service
Requires=arr-suite-network.service

[Container]
Image=docker.io/jc21/nginx-proxy-manager:latest
ContainerName=nginx-proxy-manager
PublishPort=80:80
PublishPort=443:443
PublishPort=81:81
Network=arr-suite.network
Volume=/home/user/arr-suite/config/npm/data:/data:z
Volume=/home/user/arr-suite/config/npm/letsencrypt:/etc/letsencrypt:z
Environment=TZ=America/Chicago
Label=io.containers.autoupdate=registry

[Service]
Restart=always

[Install]
WantedBy=default.target
```

## Nginx Proxy Manager Setup

NPM uses a web UI instead of container labels or config files.

1. Start NPM, then browse to `http://<host-ip>:81`
2. Default credentials: `admin@example.com` / `changeme` (change immediately)
3. Add proxy hosts via **Hosts → Proxy Hosts → Add Proxy Host**:
   - **Domain**: `sonarr.yourdomain.com`
   - **Scheme**: `http`
   - **Forward Hostname**: `sonarr` (container name on `arr-suite` network)
   - **Forward Port**: `8989`
   - **SSL tab**: Request Let's Encrypt cert, enable Force SSL + HSTS

Repeat for each service. Use container names as forward hostnames since all services share the `arr-suite` network.

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
- **Network isolation**: Services communicate on internal network; only NPM exposes external ports 80/443
- **Automatic SSL**: Let's Encrypt certs managed through NPM web UI
- **Auto-updates**: `io.containers.autoupdate=registry` label enables `podman auto-update`

## Startup Dependency Order

1. `arr-suite-network.service` (Podman network)
2. `nginx-proxy-manager.service` (can start early)
3. `qbittorrent.service` + `prowlarr.service` (download client + indexers)
4. `sonarr.service` + `radarr.service` + `lidarr.service` + `readarr.service` (media managers)
5. `bazarr.service` (subtitles, needs Sonarr/Radarr)
6. `jellyfin.service` (media server)

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
mkdir -p ~/arr-suite/config/{sonarr,radarr,lidarr,readarr,prowlarr,qbittorrent,bazarr,jellyfin,npm/data,npm/letsencrypt,n8n,audiobookshelf}

# 3. Copy quadlet files to systemd user path
mkdir -p ~/.config/containers/systemd/
cp ~/arr-suite/quadlets/*.container ~/.config/containers/systemd/
cp ~/arr-suite/quadlets/*.network ~/.config/containers/systemd/

# 4. Reload systemd and start
systemctl --user daemon-reload
systemctl --user start arr-suite-network
systemctl --user start nginx-proxy-manager
systemctl --user start prowlarr qbittorrent
systemctl --user start sonarr radarr lidarr readarr
systemctl --user start bazarr jellyfin

# 5. Enable auto-update
systemctl --user enable --now podman-auto-update.timer

# 6. Configure proxy hosts in NPM UI at http://<host>:81
```

## Firewall Rules (firewalld)

```bash
# NPM ports
sudo firewall-cmd --permanent --add-port=80/tcp
sudo firewall-cmd --permanent --add-port=443/tcp
sudo firewall-cmd --permanent --add-port=81/tcp
# RustDesk
sudo firewall-cmd --permanent --add-port=21115-21119/tcp
sudo firewall-cmd --permanent --add-port=21116/udp
sudo firewall-cmd --reload
```

## Reference

- Source article: "Building a Complete Self-Hosted Media Automation Suite with Podman Quadlets" by Miklós Galicz (Medium, Oct 2025)
- Template repo: https://codeberg.org/blackfyre/arr-suite
- Podman Quadlets docs: https://docs.podman.io/en/latest/markdown/podman-systemd.unit.5.html
- NPM docs: https://nginxproxymanager.com/guide/
