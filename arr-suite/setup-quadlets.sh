#!/usr/bin/env bash
set -euo pipefail

QUADLETS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/quadlets" && pwd)"
SYSTEMD_USER_DIR="$HOME/.config/containers/systemd"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

info()  { echo -e "${GREEN}[INFO]${NC} $*"; }
warn()  { echo -e "${YELLOW}[WARN]${NC} $*"; }
error() { echo -e "${RED}[ERROR]${NC} $*" >&2; }

discover_services() {
    find "$QUADLETS_DIR" -name "*.container" -printf "%f\n" | sed 's/\.container$//' | sort
}

discover_networks() {
    find "$QUADLETS_DIR" -name "*.network" -printf "%f\n" | sed 's/\.network$//' | sort
}

get_requires() {
    local service="$1"
    local file="$QUADLETS_DIR/$service.container"
    grep -E '^Requires=' "$file" 2>/dev/null | sed 's/Requires=//' | tr ' ' '\n' | grep '\.service$' | sed 's/\.service$//' || true
}

get_ports() {
    local service="$1"
    local file="$QUADLETS_DIR/$service.container"
    grep -E '^PublishPort=' "$file" 2>/dev/null | sed 's/PublishPort=//' | awk -F: '{print $1}' || true
}

topo_sort() {
    local services=("$@")
    local sorted=()
    local visited=()

    visit() {
        local svc="$1"
        if printf '%s\n' "${visited[@]:-}" | grep -qx "$svc"; then return; fi
        visited+=("$svc")
        for dep in $(get_requires "$svc"); do
            if printf '%s\n' "${services[@]}" | grep -qx "$dep"; then
                visit "$dep"
            fi
        done
        sorted+=("$svc")
    }

    for s in "${services[@]}"; do visit "$s"; done
    echo "${sorted[@]}"
}

cmd_setup() {
    info "Setting up arr-suite quadlets..."
    mkdir -p "$SYSTEMD_USER_DIR"

    for net in $(discover_networks); do
        local src="$QUADLETS_DIR/$net.network"
        local dst="$SYSTEMD_USER_DIR/$net.network"
        if [[ ! -L "$dst" ]] || [[ "$(readlink "$dst")" != "$src" ]]; then
            ln -sf "$src" "$dst"
            info "Linked network: $net"
        fi
    done

    for svc in $(discover_services); do
        local src="$QUADLETS_DIR/$svc.container"
        local dst="$SYSTEMD_USER_DIR/$svc.container"
        if [[ ! -L "$dst" ]] || [[ "$(readlink "$dst")" != "$src" ]]; then
            ln -sf "$src" "$dst"
            info "Linked service: $svc"
        fi
    done

    systemctl --user daemon-reload
    info "systemd daemon reloaded"

    if command -v firewall-cmd &>/dev/null; then
        info "Opening firewall ports..."
        for svc in $(discover_services); do
            for port in $(get_ports "$svc"); do
                sudo firewall-cmd --permanent --add-port="${port}/tcp" &>/dev/null && \
                    info "  Opened port $port/tcp ($svc)" || true
            done
        done
        sudo firewall-cmd --reload &>/dev/null || true
    else
        warn "firewall-cmd not found; skipping firewall setup"
    fi

    info "Setup complete."
}

cmd_start() {
    local services
    mapfile -t services < <(discover_services)
    local ordered
    read -ra ordered <<< "$(topo_sort "${services[@]}")"

    for net in $(discover_networks); do
        info "Starting network: $net"
        systemctl --user start "${net}-network.service" || warn "Network $net may already be running"
    done

    for svc in "${ordered[@]}"; do
        info "Starting: $svc"
        systemctl --user start "$svc.service"
    done
    info "All services started."
}

cmd_stop() {
    local services
    mapfile -t services < <(discover_services)
    local ordered
    read -ra ordered <<< "$(topo_sort "${services[@]}")"

    for svc in "${ordered[@]}"; do
        info "Stopping: $svc"
        systemctl --user stop "$svc.service" || true
    done

    for net in $(discover_networks); do
        info "Stopping network: $net"
        systemctl --user stop "${net}-network.service" || true
    done
    info "All services stopped."
}

cmd_restart() {
    cmd_stop
    cmd_start
}

cmd_status() {
    info "=== arr-suite status ==="
    for svc in $(discover_services); do
        local status
        status=$(systemctl --user is-active "$svc.service" 2>/dev/null || echo "inactive")
        local color="$RED"
        [[ "$status" == "active" ]] && color="$GREEN"
        echo -e "  ${color}${status}${NC}  $svc"
    done
}

cmd_ports() {
    info "=== Exposed ports ==="
    for svc in $(discover_services); do
        for port in $(get_ports "$svc"); do
            echo "  $port  →  $svc"
        done
    done
}

cmd_urls() {
    local domain="${DOMAIN:-yourdomain.com}"
    info "=== Service URLs (domain: $domain) ==="
    for svc in $(discover_services); do
        for port in $(get_ports "$svc"); do
            echo "  https://$svc.$domain  (local: http://localhost:$port)"
        done
    done
}

cmd_logs() {
    local svc="${1:-}"
    if [[ -z "$svc" ]]; then
        error "Usage: $0 logs <service>"
        exit 1
    fi
    journalctl --user -u "$svc.service" -f
}

cmd_shell() {
    local svc="${1:-}"
    if [[ -z "$svc" ]]; then
        error "Usage: $0 shell <service>"
        exit 1
    fi
    podman exec -it "$svc" /bin/bash || podman exec -it "$svc" /bin/sh
}

cmd_inspect() {
    local svc="${1:-}"
    if [[ -z "$svc" ]]; then
        error "Usage: $0 inspect <service>"
        exit 1
    fi
    podman inspect "$svc"
}

cmd="${1:-help}"
shift || true

case "$cmd" in
    setup)   cmd_setup ;;
    start)   cmd_start ;;
    stop)    cmd_stop ;;
    restart) cmd_restart ;;
    status)  cmd_status ;;
    ports)   cmd_ports ;;
    urls)    cmd_urls "$@" ;;
    logs)    cmd_logs "$@" ;;
    shell)   cmd_shell "$@" ;;
    inspect) cmd_inspect "$@" ;;
    help|*)
        echo "Usage: $0 <command> [args]"
        echo ""
        echo "Commands:"
        echo "  setup    Create systemd symlinks, reload daemon, open firewall ports"
        echo "  start    Start all services in dependency order"
        echo "  stop     Stop all services"
        echo "  restart  Restart all services"
        echo "  status   Show running status of all services"
        echo "  ports    List all exposed ports"
        echo "  urls     Generate service URLs (set DOMAIN=yourdomain.com)"
        echo "  logs     Stream logs for a service: logs <service>"
        echo "  shell    Open shell in container: shell <service>"
        echo "  inspect  Inspect container: inspect <service>"
        ;;
esac
