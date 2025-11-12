# fastapi dev backend/main.py --port 8000

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from osrswiki_images import search_many
from pydantic import BaseModel


def flatten(nested: list[list[str]]) -> list[str]:
    return [x for sub in nested for x in sub]


app = FastAPI()

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


class Sequence(BaseModel):
    sequence: list[list[str]]


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
async def create_sequence(payload: Sequence):
    seq = payload.sequence
    flat_seq = flatten(seq)
    items = search_many(flat_seq)
    return Items(items=items)


# curl -X POST \
#   -H "Content-Type: application/json" \
#   -d '{"sequence": [["a", "b"], ["c"]]}' \
#   http://127.0.0.1:8000/sequence/
