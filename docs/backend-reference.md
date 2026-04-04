# Backend Reference

This document captures backend behavior that is useful to remember when revisiting the project: exposed endpoints, request constraints, and runtime guardrails.

## Endpoints

- `POST /sequence/`
  Accepts a flat list of item names and returns item metadata gathered from the OSRS Wiki image layer.
- `POST /share/`
  Persists a share payload and returns a generated token.
- `GET /share/?token=...`
  Loads a previously saved share payload by token.
- `GET /health`
  Returns a simple health response for local and remote availability checks.

The FastAPI OpenAPI/docs routes are disabled in production code, so this file is the main lightweight endpoint reference.

## Rate Limiting

Rate limiting is enforced per client on:

- `POST /sequence/`
- `POST /share/`

Current policy:

- max 3 requests per second
- max 20 requests per minute

Client identity is resolved in this order:

- `CF-Connecting-IP`
- first IP from `X-Forwarded-For`
- socket IP from the FastAPI request
- `unknown` as a final fallback

When a client exceeds either window, the API returns:

- HTTP `429 Too Many Requests`
- `Retry-After` response header with the computed wait time in seconds

## Guardrails

### Trusted Hosts

The backend rejects requests whose `Host` header is not one of:

- `api.ladlorchart.com`
- `test.ladlorchart.com`
- `localhost`
- `127.0.0.1`

Invalid hosts receive HTTP `400`.

### Request Size Limit

The backend enforces a maximum request body size of `256 KiB`.

- Requests with too-large `Content-Length` receive HTTP `413`.
- Invalid `Content-Length` values receive HTTP `400`.

### Request Logging

Each request records:

- method
- path
- status
- latency
- client identity
- host header

Request logging is separate from best-effort endpoint analytics. Analytics write failures are logged but do not fail API responses.
