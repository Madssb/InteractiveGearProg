# Infrastructure

Explains and specifies infrastructure pertaining to services in the project
The chartbuilder relies on a backend made up of FastAPI based REST API, made accessible by tunneling from localhost:800 to 

## Syncing up project systemd units with system

0. Sync up unit files available to the OS with project ones with `sudo cp infra/systemd/* /etc/systemd/system`,
1. Scan unit files with `sudo systemctl daemon-reload`,
2. Restart services with `systemctl restart ladlor.target`





## ladlor-api.service

Starts the REST API with uv, binding to the local service endpoint 127.0.0.1:8000

## ladlor-api-tunnel.service

Sets up cloudflared to forward traffic from api.ladlorchart.com to the local service endpoint.
