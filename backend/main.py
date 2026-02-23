# fastapi dev backend/main.py --port 8000
import logging
import math
import secrets
import threading
import time
from collections import OrderedDict
from collections import defaultdict, deque
from typing import Annotated, Dict, List, Tuple

from db import load_share, save_share
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from osrswiki_images import search_many
from pydantic import BaseModel, conlist

FlatSequenceType = Annotated[list[str], conlist(str, min_length=1, max_length=500)]
NestedSequenceType = list[list[str]]


app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://ladlorchart.com",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ItemsRequest(BaseModel):
    sequence: FlatSequenceType


class ItemInfo(BaseModel):
    wikiUrl: str
    imgUrl: str
    type: str


class ItemsResponse(BaseModel):
    items: dict[str, ItemInfo]
    cacheHits: int
    cacheMisses: int


class Share(BaseModel):
    items: dict[str, ItemInfo]
    sequence: NestedSequenceType


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


CACHE: Dict[str, ItemInfo] = LRU(maxsize=5000)
RATE_LIMIT_PER_SECOND = 3
RATE_LIMIT_PER_MINUTE = 20
SEC_WINDOW_SECONDS = 1.0
MIN_WINDOW_SECONDS = 60.0
MAX_REQUEST_BODY_BYTES = 256 * 1024
ALLOWED_HOSTS = {"api.ladlorchart.com", "localhost", "127.0.0.1"}
RATE_LIMIT_LOCK = threading.Lock()
RATE_LIMIT_SEC: Dict[str, deque] = defaultdict(deque)
RATE_LIMIT_MIN: Dict[str, deque] = defaultdict(deque)
logger = logging.getLogger("backend.rate_limit")
request_logger = logging.getLogger("backend.request")


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
    if host not in ALLOWED_HOSTS:
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
            return JSONResponse(status_code=400, content={"detail": "Invalid Content-Length"})

    body = await request.body()
    if len(body) > MAX_REQUEST_BODY_BYTES:
        return JSONResponse(status_code=413, content={"detail": "Request body too large"})
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
    return response


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/sequence/")
async def create_sequence(request: Request, payload: ItemsRequest) -> ItemsResponse:
    enforce_rate_limit(request, "/sequence/")
    out: Dict[str, ItemInfo] = {}
    seq = payload.sequence
    cache_hits, cache_misses = LRU_cache(seq, CACHE)
    try:
        results = search_many(cache_misses)
    except Exception:
        # safest fallback: do not return partial API data from the wiki
        # instead return empty results for the misses
        results = {}
    for name, info in results.items():
        CACHE.put(name, info)
        out[name] = info
    for cache_hit in cache_hits:
        out[cache_hit] = CACHE[cache_hit]
    return ItemsResponse(
        items=out, cacheHits=len(cache_hits), cacheMisses=len(cache_misses)
    )


def LRU_cache(
    payload: List[str], cache: Dict[str, ItemInfo]
) -> Tuple[List[str], List[str]]:
    cache_hits: List[str] = []
    cache_misses: List[str] = []
    for entity in payload:
        if entity not in cache:
            cache_misses.append(entity)
        else:
            cache_hits.append(entity)
    return cache_hits, cache_misses


@app.post("/share/")
async def create_share(request: Request, payload: Share) -> str:
    enforce_rate_limit(request, "/share/")
    token = secrets.token_urlsafe(8)
    plain_items = {k: v.dict() for k, v in payload.items.items()}
    await save_share(token, payload.sequence, plain_items)
    return token


@app.get("/share/")
async def load_share_endpoint(token: str) -> Share:
    result = await load_share(token)
    if result is None:
        raise HTTPException(status_code=404, detail="Not found")
    sequence, items = result
    return Share(sequence=sequence, items=items)


@app.get("/health")
def health():
    return {"status": "ok"}
