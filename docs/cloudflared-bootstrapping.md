# Cloudflared Bootstrapping

This document describes setting up a cloudflared tunnel with passing `CLOUDFLARED_TUNNEL_TOKEN` to the `cloudflare/cloudflared:latest` image used in `compose.yml`. This makes compose.yml bring the backend to `VITE_API_BASE_URL`.

1. from <dash.Cloudflare.com> click on "Zero Trust" under "Protect & Connect"
2. click on "Networks" to show the dropdown menu and select "Connectors"
3. click on create a tunnel, select "Cloudflared" as the tunnel type
4. name the tunnel
5. Select your device's operating system: Docker
6. copy generated token (i.e. bit after `--token`) to `CLOUDFLARED_TUNNEL_TOKEN` in `.env`
7. set the hostname. This is what `VITE_API_BASE_URL` must match.
8. set the service as `HTTP://backend:8000`
9. click "Complete setup" to complete the setup

Backend deloyment with `compose.yml` now makes the repo endpoints available at `VITE_API_BASE_URL`.
