#!/usr/bin/env bash
set -Eeuo pipefail

# Run this on the server as root after confirming the SSH port is 22. It keeps
# database, Qdrant, Flowise and Adapter ports private to Docker's bridge.
command -v ufw >/dev/null || { printf '%s\n' 'ufw is required'; exit 1; }
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp comment 'SSH'
ufw allow 80/tcp comment 'HTTP'
ufw allow 443/tcp comment 'HTTPS'
ufw --force enable
ufw status verbose
