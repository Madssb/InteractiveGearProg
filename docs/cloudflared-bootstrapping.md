# Cloudflared Bootstrapping

This document describes setting up a cloudflared tunnel with passing `CLOUDFLARED_TUNNEL_TOKEN` to the `cloudflare/cloudflared:latest` image used in `compose.yml`. This makes compose bring the backend to the API hostname used by the frontend runtime host mapping.

1. from <dash.Cloudflare.com> click on "Zero Trust" under "Protect & Connect"
2. click on "Networks" to show the dropdown menu and select "Connectors"
3. click on create a tunnel, select "Cloudflared" as the tunnel type
4. name the tunnel
5. Select your device's operating system: Docker
6. copy generated token (i.e. bit after `--token`) to `CLOUDFLARED_TUNNEL_TOKEN` in `.env`
7. set the hostname to `api.ladlorchart.com`
8. set the service as `HTTP://backend:8000`
9. click "Complete setup" to complete the setup

Backend deployment with `compose.yml` now makes the repo endpoints available at `https://api.ladlorchart.com`.
