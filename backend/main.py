# fastapi dev backend/main.py --port 8000

from typing import Annotated

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from osrswiki_images import search_many
from pydantic import BaseModel, conlist

SequenceType = Annotated[list[str], conlist(str, min_items=1, max_items=500)]
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


class Items(BaseModel):
    items: dict[str, ItemInfo]


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/sequence/")
async def create_sequence(payload: Request):
    seq = payload.sequence
    items = search_many(seq)
    return Items(items=items)


# curl -X POST \
#   -H "Content-Type: application/json" \
#   -d '{"sequence": [["a", "b"], ["c"]]}' \
#   http://127.0.0.1:8000/sequence/
