# Bootstrapping for Cloudflare Tunnel implementations

This document describes bootstrapping Cloudflare Tunnel configuration files and credentials used by `cloudflared`.

The static frontend requires an accessible backend. Cloudflare Tunnel uses `cloudflared` to establish an outbound connection to Cloudflare, preventing inbound connections to the host machine, which is preferable for personal security.

The following steps bootstrap a Cloudflare Tunnel, exposing the locally hosted backend at a hostname accessible by the frontend:

- `cloudflared tunnel login` authenticates with Cloudflare and downloads credentials required for tunnel creation and DNS routing (`cert.pem`)

- `cloudflared tunnel create <tunnel-name>` creates a named tunnel and generates its credentials file. In this project, these files are `prod.json` and `test.json` in `infra/cloudflared/`, for the tunnels `ladlorchart-api` and `ladlorchart-test`, respectively.

- `cloudflared tunnel route dns <tunnel-id> <hostname>` creates a DNS record mapping the hostname to the tunnel. This project uses `api.ladlorchart.com` for `ladlorchart-api`, and `test.ladlorchart.com` for `ladlorchart-test`. IMPORTANT: prefer to use the id or else record may be created for the wrong tunnel.

The `config.yaml` file defines how requests are routed from the tunnel to local services and is referenced when instantiating tunnels. In this project, these files are `config.local.yml`, `config.prod.yml`, and `config.test.yml` in `infra/cloudflared/`. Bootstrapping is a one-time setup; running the tunnel is described separately.
