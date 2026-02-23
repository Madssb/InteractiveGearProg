from fastapi import HTTPException
from fastapi.responses import JSONResponse
import pytest
from starlette.requests import Request


def _request(path: str = "/health", headers: dict[str, str] | None = None) -> Request:
    raw = [(k.lower().encode("latin-1"), v.encode("latin-1")) for k, v in (headers or {}).items()]
    scope = {"type": "http", "method": "GET", "path": path, "headers": raw}

    async def receive():
        return {"type": "http.request", "body": b"", "more_body": False}

    return Request(scope, receive)


def _ok_response():
    return JSONResponse(status_code=200, content={"ok": True})


async def _ok_call_next(_request):
    return _ok_response()


def test_get_client_id_prefers_cloudflare_header(app_module):
    req = _request(headers={"cf-connecting-ip": "203.0.113.7", "x-forwarded-for": "198.51.100.4"})
    assert app_module.get_client_id(req) == "203.0.113.7"


@pytest.mark.anyio
async def test_trusted_host_rejects_invalid_header(app_module):
    req = _request(headers={"host": "evil.example"})
    resp = await app_module.trusted_host_middleware(req, _ok_call_next)
    assert resp.status_code == 400
    assert resp.body == b'{"detail":"Invalid host header"}'


@pytest.mark.anyio
async def test_request_size_rejects_oversized_content_length(app_module):
    req = _request(headers={"content-length": str(app_module.MAX_REQUEST_BODY_BYTES + 1)})
    resp = await app_module.request_size_limit_middleware(req, _ok_call_next)
    assert resp.status_code == 413
    assert resp.body == b'{"detail":"Request body too large"}'


@pytest.mark.anyio
async def test_request_size_rejects_invalid_content_length(app_module):
    req = _request(headers={"content-length": "not-an-int"})
    resp = await app_module.request_size_limit_middleware(req, _ok_call_next)
    assert resp.status_code == 400
    assert resp.body == b'{"detail":"Invalid Content-Length"}'


def test_rate_limit_raises_429_with_retry_after(app_module, monkeypatch):
    req = _request(path="/sequence/", headers={"cf-connecting-ip": "203.0.113.7"})
    monkeypatch.setattr(app_module, "RATE_LIMIT_PER_SECOND", 1)
    monkeypatch.setattr(app_module, "RATE_LIMIT_PER_MINUTE", 100)
    app_module.RATE_LIMIT_SEC.clear()
    app_module.RATE_LIMIT_MIN.clear()

    app_module.enforce_rate_limit(req, "/sequence/")

    try:
        app_module.enforce_rate_limit(req, "/sequence/")
        assert False, "Expected HTTPException for rate limiting"
    except HTTPException as exc:
        assert exc.status_code == 429
        assert exc.detail == "Too Many Requests"
        assert exc.headers and "Retry-After" in exc.headers
