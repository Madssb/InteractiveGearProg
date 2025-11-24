# fastapi dev backend/main.py --port 8000
import secrets
from collections import OrderedDict
from typing import Annotated, Dict, List, Tuple

from db import load_share, save_share
from fastapi import FastAPI, HTTPException
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


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/sequence/")
async def create_sequence(payload: ItemsRequest) -> ItemsResponse:
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
async def create_share(payload: Share) -> str:
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
