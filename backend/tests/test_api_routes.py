from types import SimpleNamespace

import pytest
from fastapi import HTTPException
from starlette.requests import Request


def _request(path: str, headers: dict[str, str] | None = None) -> Request:
    raw_headers = [(k.lower().encode("latin-1"), v.encode("latin-1")) for k, v in (headers or {}).items()]
    scope = {"type": "http", "method": "POST", "path": path, "headers": raw_headers}

    async def receive():
        return {"type": "http.request", "body": b"", "more_body": False}

    return Request(scope, receive)


def test_health_route_returns_ok(app_module):
    """Health endpoint contract: service reports simple up-state payload."""
    assert app_module.health() == {"status": "ok"}


@pytest.mark.anyio
async def test_milestone_metadata_route_returns_expected_shape_with_mocked_resolver(app_module, monkeypatch):
    """Metadata route should return typed item payload shape when resolver succeeds."""
    monkeypatch.setattr(app_module, "enforce_rate_limit", lambda request, route: None)

    def fake_query_milestone_metadata(names):
        return SimpleNamespace(
            milestoneMetadata={
                n: app_module.ItemInfo(
                    wikiUrl=f"https://oldschool.runescape.wiki/w/{n.replace(' ', '_')}",
                    imgUrl=f"https://oldschool.runescape.wiki/images/{n.replace(' ', '_')}.png",
                    type="item",
                )
                for n in names
            },
            unresolvedMilestones=[],
        )

    monkeypatch.setattr(app_module, "query_milestone_metadata", fake_query_milestone_metadata)

    req = _request("/fetch-milestone-metadata/", headers={"host": "localhost"})
    response = await app_module.populate_milestone_metadata(req, ["Amulet of strength"])

    assert response.cacheMisses == 1
    assert response.cacheHits == 0
    assert "Amulet of strength" in response.milestoneMetadata
    assert response.milestoneMetadata["Amulet of strength"].type == "item"


@pytest.mark.anyio
async def test_milestone_metadata_route_returns_cache_hits(app_module, monkeypatch):
    """Metadata route should serve repeated milestones from cache."""
    monkeypatch.setattr(app_module, "enforce_rate_limit", lambda request, route: None)
    app_module.CACHE.put(
        "Amulet of strength",
        app_module.ItemInfo(
            wikiUrl="https://oldschool.runescape.wiki/w/Amulet_of_strength",
            imgUrl="https://oldschool.runescape.wiki/images/Amulet_of_strength.png",
            type="item",
        ),
    )

    def fake_query_milestone_metadata(names):
        assert names == []
        return app_module.MilestoneMetadataQueryResult(
            milestoneMetadata={},
            unresolvedMilestones=[],
        )

    monkeypatch.setattr(app_module, "query_milestone_metadata", fake_query_milestone_metadata)

    req = _request("/fetch-milestone-metadata/", headers={"host": "localhost"})
    response = await app_module.populate_milestone_metadata(req, ["Amulet of strength"])

    assert response.cacheMisses == 0
    assert response.cacheHits == 1
    assert response.milestoneMetadata["Amulet of strength"].type == "item"


@pytest.mark.anyio
async def test_share_create_route_returns_token_and_calls_save(app_module, monkeypatch):
    """Share creation should mint token and persist normalized sequence payload."""
    monkeypatch.setattr(app_module, "enforce_rate_limit", lambda request, route: None)

    captured = {}

    async def fake_save_share(token, sequence):
        captured["token"] = token
        captured["sequence"] = sequence

    monkeypatch.setattr(app_module, "save_share", fake_save_share)
    monkeypatch.setattr(app_module.secrets, "token_urlsafe", lambda n: "tok12345")

    req = _request("/share/", headers={"host": "localhost"})
    payload = [["Amulet of strength"]]
    token = await app_module.create_share(req, payload)

    assert token == "tok12345"
    assert captured["token"] == "tok12345"
    assert captured["sequence"] == [["Amulet of strength"]]


@pytest.mark.anyio
async def test_share_load_route_success_and_not_found(app_module, monkeypatch):
    """Share loader should return payload for known token and 404 when missing."""
    async def fake_load_share_success(token):
        assert token == "abc123"
        return [["Amulet of strength"]]

    monkeypatch.setattr(app_module, "load_share", fake_load_share_success)
    share = await app_module.load_share_endpoint("abc123")
    assert share == [["Amulet of strength"]]

    async def fake_load_share_missing(token):
        return None

    monkeypatch.setattr(app_module, "load_share", fake_load_share_missing)
    with pytest.raises(HTTPException) as exc:
        await app_module.load_share_endpoint("missing")
    assert exc.value.status_code == 404
