"""Backend API endpoints consumed by Ladlorchart frontend.
"""
# fastapi dev backend/main.py --port 8000
import os
import logging
import math
import secrets
import threading
import time
from load_dotenv immport load_dotenv
from collections import OrderedDict, defaultdict, deque
from typing import Annotated, Dict, List, Tuple
from datetime import date
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, conlist

from db import (
    load_share,
    milestone_annotations_lookup,
    milestones_completed_snapshots,
    milestones_hidden_snapshots,
    save_share,
    update_endpoint_hits,
)
from osrs_milestone_metadata import (
    MilestoneMetadataQueryResult,
    MilestoneMetadataRecord,
    query_milestone_metadata,
)
from milestones import load_milestone_ids_by_name


# constants

ROOT_DIR = Path(__file__).resolve().parent.parent

load_dotenv(ROOT_DIR / ".env")

CORS_ALLOWED_ORIGINS = os.getenv("CORS_ALLOWED_ORIGINS")
if not CORS_ALLOWED_ORIGINS:
    raise SystemExit("CORS_ALLOWED_ORIGINS is not set")

TRUSTED_HOSTS = os.getenv("TRUSTED_HOSTS")
if not TRUSTED_HOSTS:
    raise SystemExit("TRUSTED_HOSTS is not set")

# types

FlatSequenceType = Annotated[list[str], conlist(str, min_length=1, max_length=500)]
NestedSequenceType = list[list[str]]

MilestoneSequence = list[list[str]]
Milestones = list[str]


class MilestoneMetadataResponse(BaseModel):
    milestoneMetadata: dict[str, MilestoneMetadataRecord]
    cacheHits: int
    cacheMisses: int


class ShareCreate(BaseModel):
    milestoneSequence: NestedSequenceType | None = None
    sequence: NestedSequenceType | None = None


class MilestoneAnnotationResponse(BaseModel):
    """Schema for GET annotations/
    """
    annotation_id: int
    up_count: int
    down_count: int
    chart_version: str
    annotation_text: str
    user_display_name: str
    created_at: date


class LRU(OrderedDict):
    def __init__(self, maxsize: int):
        super().__init__()
        self.maxsize = maxsize

    def put(self, key, value):
        if key in self:
            self.move_to_end(key)
        self[key] = value
        if len(self) > self.maxsize:
            self.popitem(last=False)

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)

# CORS

allowed_origins = [
    origin.strip()
    for origin in CORS_ALLOWED_ORIGINS.split(",")
    if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)



CACHE: Dict[str, MilestoneMetadataRecord] = LRU(maxsize=5000)
MILESTONE_IDS_BY_NAME = load_milestone_ids_by_name()
RATE_LIMIT_PER_SECOND = 3
RATE_LIMIT_PER_MINUTE = 20
SEC_WINDOW_SECONDS = 1.0
MIN_WINDOW_SECONDS = 60.0
MAX_REQUEST_BODY_BYTES = 256 * 1024
RATE_LIMIT_LOCK = threading.Lock()
RATE_LIMIT_SEC: Dict[str, deque] = defaultdict(deque)
RATE_LIMIT_MIN: Dict[str, deque] = defaultdict(deque)
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


def LRU_cache(
    payload: List[str], cache: Dict[str, MilestoneMetadataRecord]
) -> Tuple[List[str], List[str]]:
    cache_hits: List[str] = []
    cache_misses: List[str] = []
    for entity in payload:
        if entity not in cache:
            cache_misses.append(entity)
        else:
            cache_hits.append(entity)
    return cache_hits, cache_misses


# endpoints


@app.post("/fetch-milestone-metadata/")
async def populate_milestone_metadata(request: Request, milestones: Milestones) -> MilestoneMetadataResponse:
    """
    """
    enforce_rate_limit(request, "/sequence/")
    out: Dict[str, MilestoneMetadataRecord] = {}
    cache_hits, cache_misses = LRU_cache(milestones, CACHE)
    try:
        results = query_milestone_metadata(cache_misses)
    except Exception:
        results = MilestoneMetadataQueryResult(
            milestoneMetadata={},
            unresolvedMilestones=[]
        )
    for milestone, metadata in results.milestoneMetadata.items():
        CACHE.put(milestone, metadata)
        out[milestone] = metadata
    for cache_hit in cache_hits:
        out[cache_hit] = CACHE[cache_hit]
    return MilestoneMetadataResponse(
        milestoneMetadata=out, cacheHits=len(cache_hits), cacheMisses=len(cache_misses)
    )


@app.post("/share/")
async def create_share(request: Request, milestone_sequence: MilestoneSequence) -> str:
    """Instantiate chartbuilder-share record
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
    """
    milestone_sequence = await load_share(token)
    if milestone_sequence is None:
        raise HTTPException(status_code=404, detail="Token Not found")
    return milestone_sequence


@app.post("/submit-progress-snapshot")
async def submit_progress_snapshot(request: Request, milestones_completed: Milestones):
    """Retrieve completed milestones from ChartPage on load.
    """
    if not milestones_completed:
        return 
    enforce_rate_limit(request, "/submit-progress-snapshot")
    await milestones_completed_snapshots(milestones_completed)


@app.post("/submit-hidden-milestones-snapshot")
async def submit_hidden_milestones_snapshot(request: Request, milestones_hidden: Milestones):
    """Retrieve hidden milestones from ChartPage on load."""
    if not milestones_hidden:
        return
    enforce_rate_limit(request, "/submit-hidden-milestones-snapshot")
    await milestones_hidden_snapshots(milestones_hidden)


@app.get("/annotations", response_model=list[MilestoneAnnotationResponse])
async def fetch_milestone_annotations(request: Request, milestone_id: int):
    """Fetch annotations for milestone. omit annotations with ongoing reports.
    """
    enforce_rate_limit(request, "/annotations")
    return await milestone_annotations_lookup(milestone_id)


@app.get("/health")
def health():
    """Healthcheck
    """
    return {"status": "ok"}
