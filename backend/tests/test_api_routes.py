from types import SimpleNamespace

import pytest
from fastapi import HTTPException
from starlette.requests import Request


def _request(path: str, headers: dict[str, str] | None = None) -> Request:
    raw_headers = [
        (k.lower().encode("latin-1"), v.encode("latin-1"))
        for k, v in (headers or {}).items()
    ]
    scope = {"type": "http", "method": "POST", "path": path, "headers": raw_headers}

    async def receive():
        return {"type": "http.request", "body": b"", "more_body": False}

    return Request(scope, receive)


def test_health_route_returns_ok(app_module):
    """Health endpoint contract: service reports simple up-state payload."""
    assert app_module.health() == {"status": "ok"}


@pytest.mark.anyio
async def test_milestone_metadata_route_accepts_metadata_record_values(
    app_module, monkeypatch
):
    """Metadata route should accept resolver metadata record values."""
    monkeypatch.setattr(app_module, "enforce_rate_limit", lambda request, route: None)

    record = app_module.MilestoneMetadataRecord(
        wikiUrl="https://oldschool.runescape.wiki/w/Dragon_scimitar",
        imgUrl="https://oldschool.runescape.wiki/images/Dragon_scimitar.png",
        type="item",
    )

    def fake_query_milestone_metadata(names):
        assert names == ["dragon scimitar"]
        return app_module.MilestoneMetadataQueryResult(
            milestoneMetadata={"dragon scimitar": record},
            unresolvedMilestones=[],
        )

    monkeypatch.setattr(
        app_module, "query_milestone_metadata", fake_query_milestone_metadata
    )

    req = _request("/fetch-milestone-metadata/", headers={"host": "localhost"})
    response = await app_module.populate_milestone_metadata(req, ["dragon scimitar"])

    assert str(response.milestoneMetadata["dragon scimitar"].wikiUrl) == (
        "https://oldschool.runescape.wiki/w/Dragon_scimitar"
    )


@pytest.mark.anyio
async def test_milestone_metadata_route_returns_expected_shape_with_mocked_resolver(
    app_module, monkeypatch
):
    """Metadata route should return typed item payload shape when resolver succeeds."""
    monkeypatch.setattr(app_module, "enforce_rate_limit", lambda request, route: None)

    def fake_query_milestone_metadata(names):
        return SimpleNamespace(
            milestoneMetadata={
                n: app_module.MilestoneMetadataRecord(
                    wikiUrl=f"https://oldschool.runescape.wiki/w/{n.replace(' ', '_')}",
                    imgUrl=f"https://oldschool.runescape.wiki/images/{n.replace(' ', '_')}.png",
                    type="item",
                )
                for n in names
            },
            unresolvedMilestones=[],
        )

    monkeypatch.setattr(
        app_module, "query_milestone_metadata", fake_query_milestone_metadata
    )

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
        app_module.MilestoneMetadataRecord(
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

    monkeypatch.setattr(
        app_module, "query_milestone_metadata", fake_query_milestone_metadata
    )

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


@pytest.mark.anyio
async def test_submit_progress_snapshot_enforces_rate_limit_and_persists(
    app_module, monkeypatch
):
    """Progress snapshots should be rate-limited and persisted as completed milestones."""
    calls = {}

    def fake_enforce_rate_limit(request, route):
        calls["path"] = request.url.path
        calls["route"] = route

    async def fake_milestones_completed_snapshots(milestones_completed):
        calls["milestones_completed"] = milestones_completed

    monkeypatch.setattr(app_module, "enforce_rate_limit", fake_enforce_rate_limit)
    monkeypatch.setattr(
        app_module,
        "milestones_completed_snapshots",
        fake_milestones_completed_snapshots,
    )

    req = _request("/submit-progress-snapshot", headers={"host": "localhost"})
    await app_module.submit_progress_snapshot(req, ["Amulet of strength"])

    assert calls["path"] == "/submit-progress-snapshot"
    assert calls["route"] == "/submit-progress-snapshot"
    assert calls["milestones_completed"] == ["Amulet of strength"]


@pytest.mark.anyio
async def test_submit_progress_snapshot_ignores_empty_payload(app_module, monkeypatch):
    """Empty progress snapshots should not create analytics rows."""
    calls = {"rate_limit": 0, "persist": 0}

    def fake_enforce_rate_limit(_request, _route):
        calls["rate_limit"] += 1

    async def fake_milestones_completed_snapshots(_milestones_completed):
        calls["persist"] += 1

    monkeypatch.setattr(app_module, "enforce_rate_limit", fake_enforce_rate_limit)
    monkeypatch.setattr(
        app_module,
        "milestones_completed_snapshots",
        fake_milestones_completed_snapshots,
    )

    req = _request("/submit-progress-snapshot", headers={"host": "localhost"})
    assert await app_module.submit_progress_snapshot(req, []) is None

    assert calls == {"rate_limit": 0, "persist": 0}


@pytest.mark.anyio
async def test_submit_hidden_milestones_snapshot_enforces_rate_limit_and_persists(
    app_module, monkeypatch
):
    """Hidden milestone snapshots should be rate-limited and persisted."""
    calls = {}

    def fake_enforce_rate_limit(request, route):
        calls["path"] = request.url.path
        calls["route"] = route

    async def fake_milestones_hidden_snapshots(milestones_hidden):
        calls["milestones_hidden"] = milestones_hidden

    monkeypatch.setattr(app_module, "enforce_rate_limit", fake_enforce_rate_limit)
    monkeypatch.setattr(
        app_module,
        "milestones_hidden_snapshots",
        fake_milestones_hidden_snapshots,
    )

    req = _request("/submit-hidden-milestones-snapshot", headers={"host": "localhost"})
    await app_module.submit_hidden_milestones_snapshot(req, ["Dragon scimitar"])

    assert calls["path"] == "/submit-hidden-milestones-snapshot"
    assert calls["route"] == "/submit-hidden-milestones-snapshot"
    assert calls["milestones_hidden"] == ["Dragon scimitar"]


@pytest.mark.anyio
async def test_submit_hidden_milestones_snapshot_ignores_empty_payload(
    app_module, monkeypatch
):
    """Empty hidden milestone snapshots should not create analytics rows."""
    calls = {"rate_limit": 0, "persist": 0}

    def fake_enforce_rate_limit(_request, _route):
        calls["rate_limit"] += 1

    async def fake_milestones_hidden_snapshots(_milestones_hidden):
        calls["persist"] += 1

    monkeypatch.setattr(app_module, "enforce_rate_limit", fake_enforce_rate_limit)
    monkeypatch.setattr(
        app_module,
        "milestones_hidden_snapshots",
        fake_milestones_hidden_snapshots,
    )

    req = _request("/submit-hidden-milestones-snapshot", headers={"host": "localhost"})
    assert await app_module.submit_hidden_milestones_snapshot(req, []) is None

    assert calls == {"rate_limit": 0, "persist": 0}


@pytest.mark.anyio
async def test_submit_annotation_view_event_enforces_rate_limit_and_persists(
    app_module, monkeypatch
):
    """Annotation views should be rate-limited and persisted by milestone name."""
    calls = {}

    def fake_enforce_rate_limit(request, route):
        calls["path"] = request.url.path
        calls["route"] = route

    async def fake_annotation_view_event(milestone_name):
        calls["milestone_name"] = milestone_name

    monkeypatch.setattr(app_module, "enforce_rate_limit", fake_enforce_rate_limit)
    monkeypatch.setattr(
        app_module,
        "annotation_view_event",
        fake_annotation_view_event,
    )

    req = _request("/submit-annotation-view-event", headers={"host": "localhost"})
    event = app_module.AnnotationViewEventCreate(milestone_name=" Dragon scimitar ")
    await app_module.submit_annotation_view_event(req, event)

    assert calls["path"] == "/submit-annotation-view-event"
    assert calls["route"] == "/submit-annotation-view-event"
    assert calls["milestone_name"] == "Dragon scimitar"


@pytest.mark.anyio
async def test_submit_annotation_view_event_ignores_blank_payload(
    app_module, monkeypatch
):
    """Blank annotation view names should not create analytics rows."""
    calls = {"rate_limit": 0, "persist": 0}

    def fake_enforce_rate_limit(_request, _route):
        calls["rate_limit"] += 1

    async def fake_annotation_view_event(_milestone_name):
        calls["persist"] += 1

    monkeypatch.setattr(app_module, "enforce_rate_limit", fake_enforce_rate_limit)
    monkeypatch.setattr(
        app_module,
        "annotation_view_event",
        fake_annotation_view_event,
    )

    req = _request("/submit-annotation-view-event", headers={"host": "localhost"})
    event = app_module.AnnotationViewEventCreate(milestone_name="   ")
    assert await app_module.submit_annotation_view_event(req, event) is None

    assert calls == {"rate_limit": 0, "persist": 0}


@pytest.mark.anyio
async def test_fetch_skip_pcts_caches_bulk_skip_rates(app_module, monkeypatch):
    calls = {"skip_rates": 0}

    def fake_enforce_rate_limit(request, route):
        calls["path"] = request.url.path
        calls["route"] = route

    def fake_main_sequence_skip_contexts():
        return {"A": (["B", "C"], 1)}

    async def fake_milestone_skip_rates(contexts, start_time, stop_time):
        calls["skip_rates"] += 1
        calls["contexts"] = contexts
        assert start_time < stop_time
        return {
            "A": {
                "skipped_count": 1,
                "eligible_count": 2,
                "skip_rate": 0.5,
            },
        }

    monkeypatch.setattr(app_module, "enforce_rate_limit", fake_enforce_rate_limit)
    monkeypatch.setattr(
        app_module,
        "main_sequence_skip_contexts",
        fake_main_sequence_skip_contexts,
    )
    monkeypatch.setattr(
        app_module,
        "milestone_skip_rates",
        fake_milestone_skip_rates,
    )
    app_module.SKIP_PCTS["data"] = None

    req = _request("/skip-pcts", headers={"host": "localhost"})
    first = await app_module.fetch_skip_pcts(req)
    second = await app_module.fetch_skip_pcts(req)

    assert calls["path"] == "/skip-pcts"
    assert calls["route"] == "/skip-pcts"
    assert calls["contexts"] == {"A": (["B", "C"], 1)}
    assert calls["skip_rates"] == 1
    assert first == second
