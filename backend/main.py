# fastapi dev backend/main.py --port 8000

from collections import OrderedDict
from typing import Annotated, Dict, List, Tuple

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from osrswiki_images import search_many
from pydantic import BaseModel, conlist

SequenceType = Annotated[list[str], conlist(str, min_length=1, max_length=50)]
# Autodocs is considered risky.
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


class Request(BaseModel):
    sequence: SequenceType


class ItemInfo(BaseModel):
    wikiUrl: str
    imgUrl: str
    type: str


class Response(BaseModel):
    items: dict[str, ItemInfo]
    cacheHits: int
    cacheMisses: int


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
async def create_sequence(payload: Request):
    out: Dict[str, ItemInfo] = {}
    seq = payload.sequence
    cache_hits, cache_misses = LRU_cache(seq, CACHE)
    results = search_many(cache_misses)
    for name, info in results.items():
        CACHE.put(name, info)
        out[name] = info
    for cache_hit in cache_hits:
        out[cache_hit] = CACHE[cache_hit]
    return Response(items=out, cacheHits=len(cache_hits), cacheMisses=len(cache_misses))


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


# curl -X POST \
#   -H "Content-Type: application/json" \
#   -d '{"sequence": [["a", "b"], ["c"]]}' \
#   http://127.0.0.1:8000/sequence/
