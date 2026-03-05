# Infrastructure

Explains and specifies infrastructure pertaining to services the project makes use of in production.
The chartbuilder relies on a backend made up of FastAPI based REST API, made accessible by tunneling from localhost:8000 to api.ladlorchart.com 

## Systemd

systemd units keeps the REST API running locally on my server and tunnels it through cloudflare.

* sync unit templates with system: `sudo cp infra/systemd/* /etc/systemd/system && systemctl daemon-reload`
* start/stop/restart/status: `sudo systemctl start/stop/restart/status ladlor.target`

## Cloudflared Tunnel

Sets up tunnel from custom domain to local REST API. For implementation details follow guide: [https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/do-more-with-tunnels/local-management/as-a-service/linux/]
