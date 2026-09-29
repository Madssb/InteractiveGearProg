"""Backend API endpoints consumed by Ladlorchart frontend.

Partially broken after the osrs wiki do not want to be a dependency of the chart.
"""

# fastapi dev backend/main.py --port 8000
import json
import logging
import math
import os
import secrets
import threading
import time
from collections import defaultdict, deque
from datetime import datetime, timedelta
from itertools import chain
from typing import Annotated, TypedDict
from zoneinfo import ZoneInfo

from dotenv import load_dotenv
from fastapi import Body, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse

from backend.assets import item_icon_path
from backend.database.analytics import update_endpoint_hits
from backend.database.annotations import (
    AnnotationRecord,
    annotation_view_event,
    fetch_annotation_visibility_statuses,
    milestone_annotation_view_counts,
    milestone_annotations_lookup,
)
from backend.database.chart_analytics import (
    CompletionMetrics,
    SkipMetrics,
    get_visit_count,
    milestone_completion_rates,
)
from backend.database.chartbuilder import (
    insert_asset,
    load_share,
    lookup_asset,
    save_share,
)
from backend.database.snapshots import (
    record_completed_milestones_snapshot,
    record_hidden_milestones_snapshot,
)
from backend.milestones import (
    fetch_skip_metrics,
    load_main_milestone_groups,
)
from shared.paths import ENV_PATH, MAIN_SEQUENCE_PATH, RETIREMENT_SEQUENCE_PATH

# constants
with MAIN_SEQUENCE_PATH.open() as r:
    MAIN_SEQUENCE = json.load(r)
with RETIREMENT_SEQUENCE_PATH.open() as r:
    RETIREMENT_SEQUENCE = json.load(r)

MAIN_SEQUENCE_GROUPS = load_main_milestone_groups()
RETIREMENT_SEQUENCE_GROUPS = [
    [milestone.removeprefix("*") for milestone in group]
    for group in RETIREMENT_SEQUENCE
]
MAIN_SEQUENCE_FLAT = list(chain.from_iterable(MAIN_SEQUENCE_GROUPS))
RETIREMENT_SEQUENCE_FLAT = list(chain.from_iterable(RETIREMENT_SEQUENCE_GROUPS))
COMBINED_SEQUENCE_FLAT = MAIN_SEQUENCE_FLAT + RETIREMENT_SEQUENCE_FLAT

load_dotenv(ENV_PATH)

CORS_ALLOWED_ORIGINS = os.getenv("CORS_ALLOWED_ORIGINS")
if not CORS_ALLOWED_ORIGINS:
    raise SystemExit("CORS_ALLOWED_ORIGINS is not set")


def parse_trusted_hosts(raw: str) -> set[str]:
    return {host.strip().lower() for host in raw.split(",") if host.strip()}


TRUSTED_HOSTS = parse_trusted_hosts(os.getenv("TRUSTED_HOSTS", ""))
if not TRUSTED_HOSTS:
    raise SystemExit("TRUSTED_HOSTS is not set")

# types

MilestoneSequence = list[list[str]]  # grouping-aware
Milestones = list[str]


class ChartbuilderMetadataRecord(TypedDict):
    imgUrl: str
    wikiUrl: str


class ChartbuilderMetadataResponse(TypedDict):
    resolved: dict[str, ChartbuilderMetadataRecord]
    unresolved: list[str]


app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)

# CORS

allowed_origins = [
    origin.strip() for origin in CORS_ALLOWED_ORIGINS.split(",") if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)


RATE_LIMIT_PER_SECOND = 3
RATE_LIMIT_PER_MINUTE = 20
SEC_WINDOW_SECONDS = 1.0
MIN_WINDOW_SECONDS = 60.0
MAX_REQUEST_BODY_BYTES = 256 * 1024
RATE_LIMIT_LOCK = threading.Lock()
RATE_LIMIT_SEC: dict[str, deque] = defaultdict(deque)
RATE_LIMIT_MIN: dict[str, deque] = defaultdict(deque)
OSLO = ZoneInfo("Europe/Oslo")
COMPLETION_PCTS = {
    "data": None,
    "date": datetime.now(OSLO).date(),
}
SKIP_PCTS = {
    "data": None,
    "date": datetime.now(OSLO).date(),
}
VIEWCOUNT = {
    "data": None,
    "date": datetime.now(OSLO).date(),
}
logger = logging.getLogger("backend.rate_limit")
request_logger = logging.getLogger("backend.request")
analytics_logger = logging.getLogger("backend.analytics")


def get_client_id(request: Request) -> str:
    cf_ip = request.headers.get("cf-connecting-ip")
    if cf_ip:
        return cf_ip.strip()
    xff = request.headers.get("x-forwarded-for")
    if xff:
        # first IP in list is original client
        return xff.split(",")[0].strip()
    if request.client and request.client.host:
        return request.client.host
    return "unknown"


def enforce_rate_limit(request: Request, route_name: str) -> None:
    now = time.monotonic()
    client_id = get_client_id(request)
    key = f"{route_name}:{client_id}"
    with RATE_LIMIT_LOCK:
        sec_q = RATE_LIMIT_SEC[key]
        min_q = RATE_LIMIT_MIN[key]

        while sec_q and now - sec_q[0] >= SEC_WINDOW_SECONDS:
            sec_q.popleft()
        while min_q and now - min_q[0] >= MIN_WINDOW_SECONDS:
            min_q.popleft()

        if len(sec_q) >= RATE_LIMIT_PER_SECOND or len(min_q) >= RATE_LIMIT_PER_MINUTE:
            next_sec = SEC_WINDOW_SECONDS - (now - sec_q[0]) if sec_q else 0.0
            next_min = MIN_WINDOW_SECONDS - (now - min_q[0]) if min_q else 0.0
            retry_after = max(1, math.ceil(max(next_sec, next_min)))
            logger.warning(
                "rate_limited client=%s route=%s sec=%s min=%s retry_after=%s",
                client_id,
                route_name,
                len(sec_q),
                len(min_q),
                retry_after,
            )
            raise HTTPException(
                status_code=429,
                detail="Too Many Requests",
                headers={"Retry-After": str(retry_after)},
            )

        sec_q.append(now)
        min_q.append(now)


@app.middleware("http")
async def trusted_host_middleware(request: Request, call_next):
    host_header = request.headers.get("host", "")
    host = host_header.split(":")[0].strip().lower()
    if host not in TRUSTED_HOSTS:
        return JSONResponse(status_code=400, content={"detail": "Invalid host header"})
    return await call_next(request)


@app.middleware("http")
async def request_size_limit_middleware(request: Request, call_next):
    content_length = request.headers.get("content-length")
    if content_length:
        try:
            if int(content_length) > MAX_REQUEST_BODY_BYTES:
                return JSONResponse(
                    status_code=413, content={"detail": "Request body too large"}
                )
        except ValueError:
            return JSONResponse(
                status_code=400, content={"detail": "Invalid Content-Length"}
            )

    return await call_next(request)


@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    start = time.perf_counter()
    client_id = get_client_id(request)
    host = request.headers.get("host", "")
    try:
        response = await call_next(request)
    except Exception:
        request_logger.exception(
            "request_failed method=%s path=%s client=%s host=%s",
            request.method,
            request.url.path,
            client_id,
            host,
        )
        raise

    duration_ms = (time.perf_counter() - start) * 1000
    request_logger.info(
        "request method=%s path=%s status=%s duration_ms=%.2f client=%s host=%s",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
        client_id,
        host,
    )
    # Best-effort analytics: never block or fail API responses.
    try:
        endpoint_key = f"{request.method} {request.url.path}"
        await update_endpoint_hits(endpoint_key)
    except Exception:
        analytics_logger.exception(
            "endpoint_hit_write_failed endpoint=%s", request.url.path
        )
    return response


@app.post("/share/")
async def create_share(request: Request, milestone_sequence: MilestoneSequence) -> str:
    """Submit chartbuilder-share record

    Args:
        request: tbd
        milestone_sequence: User submitted milestone sequence.

    Returns:
        Token that resolves milestone_sequence on lookup.
    """
    enforce_rate_limit(request, "/share/")
    if milestone_sequence is None:
        raise HTTPException(status_code=422, detail="Missing milestone sequence")
    token = secrets.token_urlsafe(8)
    await save_share(token, milestone_sequence)
    return token


@app.get("/share/")
async def load_share_endpoint(token: str) -> MilestoneSequence:
    """Retrieve `sequence` from chartbuilder-share record

    Args:
        token: Resolves user submitted milestone sequence.

    Returns:
        User submitted milestone sequence.
    """
    # Not directly affected by msm
    milestone_sequence = await load_share(token)
    if milestone_sequence is None:
        raise HTTPException(status_code=404, detail="Token Not found")
    return milestone_sequence


@app.post("/submit-progress-snapshot")
async def submit_completed_milestones_snapshot(
    request: Request, milestones_completed: list[str]
) -> None:
    """Record completed milestones.

    Args:
        request: TBD.
        milestones_completed: Milestones completed by user ordered by completion.
    """
    # milestones_completed is a list
    if not milestones_completed:
        return
    enforce_rate_limit(request, "/submit-progress-snapshot")
    await record_completed_milestones_snapshot(milestones_completed)


@app.post("/submit-hidden-milestones-snapshot")
async def submit_hidden_milestones_snapshot(
    request: Request, milestones_hidden: set[str]
) -> None:
    """Record hidden milestones.

    Args:
        request: TBD.
        milestones_hidden: Milestones hidden by user.
    """
    if not milestones_hidden:
        return
    enforce_rate_limit(request, "/submit-hidden-milestones-snapshot")
    await record_hidden_milestones_snapshot(milestones_hidden)


@app.post("/submit-annotation-view-event")
async def submit_annotation_view_event(
    request: Request,
    milestone_name: Annotated[str, Body(embed=True)],
) -> None:
    """Record milestone annotation view event.

    Args:
        request: TBD.
        milestone_name: Milestone with viewed annotation.
    """
    milestone_name = milestone_name.strip()
    if not milestone_name:
        return
    enforce_rate_limit(request, "/submit-annotation-view-event")
    await annotation_view_event(milestone_name)


@app.get("/annotations")
async def fetch_milestone_annotations(
    request: Request, milestone_id: int
) -> list[AnnotationRecord]:
    """Fetch annotations for milestone. omit annotations with ongoing reports.

    Args:
        request: TBD.
        milestone_id: Chart provisioned milestone ID.

    Returns:

    """
    enforce_rate_limit(request, "/annotations")
    return await milestone_annotations_lookup(milestone_id)


@app.get("/completion-pcts")
async def fetch_completion_pcts(request: Request) -> dict[str, CompletionMetrics]:
    """Fetch completion metrics for all milestones.

    Args:
        request: tbd.
    """
    enforce_rate_limit(request, "/completion-pcts")
    if COMPLETION_PCTS["data"] and datetime.now(OSLO).date() == COMPLETION_PCTS["date"]:
        # Avoid duplicate work.
        return COMPLETION_PCTS["data"]
    COMPLETION_PCTS["date"] = datetime.now(OSLO).date()
    now = datetime.now(OSLO)
    COMPLETION_PCTS["data"] = await milestone_completion_rates(
        COMBINED_SEQUENCE_FLAT, now - timedelta(days=7), now
    )
    return COMPLETION_PCTS["data"]


@app.get("/skip-pcts")
async def fetch_skip_pcts(request: Request) -> dict[str, SkipMetrics]:
    """Fetch skip metrics for all milestones.

    Args:
        request: TBD.
    """
    # not affected
    enforce_rate_limit(request, "/skip-pcts")
    if SKIP_PCTS["data"] and datetime.now(OSLO).date() == SKIP_PCTS["date"]:
        # Avoid duplicate work.
        return SKIP_PCTS["data"]
    SKIP_PCTS["date"] = datetime.now(OSLO).date()
    now = datetime.now(OSLO)
    SKIP_PCTS["data"] = await fetch_skip_metrics(
        now - timedelta(days=7),
        now,
    )
    return SKIP_PCTS


@app.get("/annotation-view-counts")
async def fetch_annotation_view_counts(request: Request) -> dict[str, int]:
    """Fetch annotation viewcounts.

    Args:
        request: TBD.

    Returns:
        Milestone-name:annotation-view-count key-val pairs.
    """
    enforce_rate_limit(request, "/annotation-view-counts")
    now = datetime.now(OSLO)
    return await milestone_annotation_view_counts(
        now - timedelta(days=7),
        now,
    )


@app.get("/annotation-statuses")
async def fetch_annotation_statuses(request: Request) -> set[str]:
    """Fetch chart milestones with one or more visible annotations.

    Args:
        Request: TBD.

    Returns:
        Milestones with one or more visible annotations.
    """
    enforce_rate_limit(request, "/annotation-statuses")
    return await fetch_annotation_visibility_statuses()


@app.get("/milestones-completed-count")
async def get_milestones_completed_count(request: Request, num_days: int) -> int:
    """Return viewcount as derived from ms completion set count.

    Make one db query per day for 31 days and otherwise serve the cached one. Unimplemented
    for the rest.

    Args:
        request (Request): Request for rate limiting, etc.
        num_days (int): Number of days backwards to count ms completed sets count.
    """
    enforce_rate_limit(request, "/milestones-completed-count")
    if num_days is None:
        raise HTTPException(status_code=422, detail="Missing num_days")
    if not VIEWCOUNT["data"] or datetime.now(OSLO).date() > VIEWCOUNT["date"]:
        now = datetime.now(OSLO)
        VIEWCOUNT["date"] = now.date()
        VIEWCOUNT["data"] = await get_visit_count(
            now - timedelta(days=num_days),
            now,
        )
    return VIEWCOUNT["data"]


@app.get("/chartbuilder-asset")
async def get_asset(milestone: str) -> FileResponse:
    """Get milestone icon asset if it exists in chartbuilder_assets.

    Args:
        request: tbd.
        milestone: Milestone to get icon asset for.

    Returns:
        Milestone icon asset.

    Raises:
        400 if milestone name contains commas.
        404 if milestone icon asset doesn't exist.
    """
    # enforce_rate_limit(request, "/milestones-completed-count")
    if "," in milestone:
        # reject detactable junk
        raise HTTPException(
            status_code=400,
            detail="Milestone names cannot contain commas.",
        )
    # Avoid duplicate work by checking cache.
    exists, path = await lookup_asset(milestone)
    if exists and path is not None:
        return FileResponse(path)
    raise HTTPException(status_code=404, detail="Milestone could not be found.")


@app.post("/chartbuilder-metadata")
async def get_metadata(
    request: Request, milestones: set[str]
) -> ChartbuilderMetadataResponse:
    """Fetch Chartbuilder milestone metadata from chartbuilder_assets table if it exists.

    If record is missing from chartbuilder_assets, attempt to resolve asset and record
    its success or failure.

    Args:
        request: TBD.
        milestones: Chartbuilder milestone assets to get metadata for.

    Returns:
        Chartbuilder metadata and unresolved milestones.
    """
    enforce_rate_limit(request, "/milestones-completed-count")
    metadata: dict[str, ChartbuilderMetadataRecord] = {}
    unresolved: set[str] = set()
    pat = "/chartbuilder-asset?milestone="
    wiki_base = "https://oldschool.runescape.wiki/w/"
    for milestone_ in milestones:
        milestone = milestone_.strip()
        if "," in milestone:
            # reject detectable junk early
            unresolved.add(milestone)
            continue
        record: ChartbuilderMetadataRecord = {
            "imgUrl": pat + milestone,
            "wikiUrl": wiki_base + milestone.lower().replace(" ", "_"),
        }
        # avoid duplicate work.
        exists, path = await lookup_asset(milestone)
        if exists:
            if path is not None:
                # Asset exists from previous successful fetch.
                metadata[milestone] = record
            else:
                # Previous asset fetch failed and this one would probably too.
                unresolved.add(milestone)
        else:
            try:
                path, canonical_name = item_icon_path(milestone)
                # Cache asset fetch success.
                await insert_asset(canonical_name, path)
                metadata[milestone] = record
            except ValueError:
                # Cache asset fetch failure.
                await insert_asset(milestone, None)
                unresolved.add(milestone)
    return {"resolved": metadata, "unresolved": list(unresolved)}


@app.get("/health")
def health():
    """Healthcheck"""
    return {"status": "ok"}
