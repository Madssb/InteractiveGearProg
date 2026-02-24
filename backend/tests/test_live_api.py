import asyncio
import os
from json import dumps as json_dumps
from json import load as json_load
import re
import uuid
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import asyncpg
import pytest
from dotenv import dotenv_values

DEFAULT_LIVE_API_BASE_URL = "http://127.0.0.1:8000"
DEFAULT_LIVE_VALID_SHARE_TOKEN = "0PL8AEgmydg"
TABLE_NAME_RE = re.compile(r"^[a-z_][a-z0-9_]*$")


@pytest.mark.live
def test_get_share_invalid_token_returns_404():
    """Live API check: unknown share token should return HTTP 404."""
    if os.getenv("RUN_LIVE_TESTS") != "1":
        pytest.skip("Set RUN_LIVE_TESTS=1 to run live HTTP checks.")

    base_url = os.getenv("LIVE_API_BASE_URL", DEFAULT_LIVE_API_BASE_URL)
    url = f"{base_url}/share/?token=definitely-not-a-real-token-xyz"

    with pytest.raises(HTTPError) as exc:
        urlopen(url, timeout=10)

    assert exc.value.code == 404


@pytest.mark.live
def test_get_share_valid_token_returns_200():
    """Live API check: known share token should return HTTP 200 and payload."""
    if os.getenv("RUN_LIVE_TESTS") != "1":
        pytest.skip("Set RUN_LIVE_TESTS=1 to run live HTTP checks.")

    base_url = os.getenv("LIVE_API_BASE_URL", DEFAULT_LIVE_API_BASE_URL)
    token = os.getenv("LIVE_VALID_SHARE_TOKEN", DEFAULT_LIVE_VALID_SHARE_TOKEN)
    url = f"{base_url}/share/?token={token}"

    with urlopen(url, timeout=10) as response:
        assert response.status == 200
        payload = json_load(response)

    assert "sequence" in payload
    assert "items" in payload


@pytest.mark.live
def test_post_sequence_smoke_returns_200_and_expected_shape():
    """Live API smoke check: sequence route returns expected response structure."""
    if os.getenv("RUN_LIVE_TESTS") != "1":
        pytest.skip("Set RUN_LIVE_TESTS=1 to run live HTTP checks.")

    base_url = os.getenv("LIVE_API_BASE_URL", DEFAULT_LIVE_API_BASE_URL)
    url = f"{base_url}/sequence/"
    body = json_dumps({"sequence": ["bones"]}).encode("utf-8")
    request = Request(
        url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urlopen(request, timeout=10) as response:
        assert response.status == 200
        payload = json_load(response)

    assert "items" in payload
    assert "cacheHits" in payload
    assert "cacheMisses" in payload
    assert "bones" in payload["items"]
    assert isinstance(payload["items"]["bones"]["wikiUrl"], str)
    assert isinstance(payload["items"]["bones"]["imgUrl"], str)
    assert isinstance(payload["items"]["bones"]["type"], str)
    assert payload["items"]["bones"]["wikiUrl"]
    assert payload["items"]["bones"]["imgUrl"]
    assert payload["items"]["bones"]["type"]


@pytest.mark.live
def test_post_share_roundtrip_and_cleanup():
    """Live API check: create share, fetch share, then delete inserted test row."""
    if os.getenv("RUN_LIVE_TESTS") != "1":
        pytest.skip("Set RUN_LIVE_TESTS=1 to run live HTTP checks.")

    database_url = _resolve_cleanup_database_url()
    if not database_url:
        pytest.skip(
            "Set LIVE_CLEANUP_DATABASE_URL or DATABASE_URL for live share cleanup."
        )

    shares_table = os.getenv("SHARES_TABLE", "shares")
    if shares_table != "shares_test":
        pytest.skip("Set SHARES_TABLE=shares_test to run mutating live share tests safely.")
    if not TABLE_NAME_RE.match(shares_table):
        pytest.skip("SHARES_TABLE has invalid format.")

    base_url = os.getenv("LIVE_API_BASE_URL", DEFAULT_LIVE_API_BASE_URL)
    url = f"{base_url}/share/"
    body = json_dumps(
        {
            "sequence": [["bones"]],
            "items": {
                "bones": {
                    "wikiUrl": "https://oldschool.runescape.wiki/w/Bones",
                    "imgUrl": "https://oldschool.runescape.wiki/images/Bones.png",
                    "type": "item",
                }
            },
        }
    ).encode("utf-8")
    request = Request(
        url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    token = None
    try:
        with urlopen(request, timeout=10) as response:
            assert response.status == 200
            token = json_load(response)
        assert isinstance(token, str)
        assert token

        with urlopen(f"{base_url}/share/?token={token}", timeout=10) as response:
            assert response.status == 200
            payload = json_load(response)
        assert payload["sequence"] == [["bones"]]
        assert "bones" in payload["items"]
    finally:
        if token:
            asyncio.run(_delete_share_row(database_url, shares_table, token))


@pytest.mark.live
def test_sequence_rate_limit_returns_429_with_retry_after():
    """Live API guardrail: burst requests should trigger 429 and Retry-After."""
    if os.getenv("RUN_LIVE_TESTS") != "1":
        pytest.skip("Set RUN_LIVE_TESTS=1 to run live HTTP checks.")

    base_url = os.getenv("LIVE_API_BASE_URL", DEFAULT_LIVE_API_BASE_URL)
    url = f"{base_url}/sequence/"
    body = json_dumps({"sequence": ["bones"]}).encode("utf-8")
    client_ip = f"198.51.100.{(uuid.uuid4().int % 200) + 1}"
    headers = {
        "Content-Type": "application/json",
        "CF-Connecting-IP": client_ip,
    }

    saw_429 = False
    for _ in range(8):
        request = Request(url, data=body, headers=headers, method="POST")
        try:
            with urlopen(request, timeout=10) as response:
                assert response.status == 200
        except HTTPError as exc:
            if exc.code == 429:
                saw_429 = True
                retry_after = exc.headers.get("Retry-After")
                assert retry_after is not None
                assert int(retry_after) >= 1
                break
            raise
    assert saw_429, "Expected at least one 429 during burst requests."


@pytest.mark.live
def test_invalid_host_header_returns_400():
    """Live API guardrail: requests with non-allowlisted Host should be rejected."""
    if os.getenv("RUN_LIVE_TESTS") != "1":
        pytest.skip("Set RUN_LIVE_TESTS=1 to run live HTTP checks.")

    base_url = os.getenv("LIVE_API_BASE_URL", DEFAULT_LIVE_API_BASE_URL)
    request = Request(f"{base_url}/health", headers={"Host": "evil.example"}, method="GET")

    with pytest.raises(HTTPError) as exc:
        urlopen(request, timeout=10)
    assert exc.value.code == 400


@pytest.mark.live
def test_oversized_body_returns_413():
    """Live API guardrail: oversized request body should be blocked with 413."""
    if os.getenv("RUN_LIVE_TESTS") != "1":
        pytest.skip("Set RUN_LIVE_TESTS=1 to run live HTTP checks.")

    base_url = os.getenv("LIVE_API_BASE_URL", DEFAULT_LIVE_API_BASE_URL)
    url = f"{base_url}/sequence/"
    body = b"x" * 1024
    headers = {
        "Content-Type": "application/json",
        "Content-Length": str(256 * 1024 + 1),
    }
    request = Request(url, data=body, headers=headers, method="POST")

    with pytest.raises(HTTPError) as exc:
        urlopen(request, timeout=10)
    assert exc.value.code == 413


async def _delete_share_row(database_url: str, shares_table: str, token: str) -> None:
    conn = await asyncpg.connect(database_url, timeout=5)
    try:
        await conn.execute(f"DELETE FROM {shares_table} WHERE token = $1", token)
    finally:
        await conn.close()


def _resolve_cleanup_database_url() -> str | None:
    """Resolve DB URL for live-test cleanup without relying on shell state only."""
    explicit = os.getenv("LIVE_CLEANUP_DATABASE_URL")
    if explicit:
        return explicit

    env_file_values = dotenv_values(".env")
    file_url = env_file_values.get("DATABASE_URL")
    if isinstance(file_url, str) and file_url:
        return file_url

    return os.getenv("DATABASE_URL")
