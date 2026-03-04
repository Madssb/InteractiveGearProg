import requests
from pydantic import BaseModel, Field
from typing import List


"""
$ curl -sS -X POST http://127.0.0.1:3000/osrs-dps/api/ttk -H 'Content-Type: application/json' -d '{"monsterId":"yama#normal","setup":{"equipment":{"weapon":"abyssal whip"}}}'
{"ttk":5449.774209796954,"dps":0.4601367138303325,"maxHit":24,"accuracy":0.09172160408578055,"attackSpeed":4,"monster":{"id":14176,"name":"Yama","version":"Normal","currentHp":2500}}
"""

dps_endpoint = "http://127.0.0.1:3000/osrs-dps/api/ttk"





gear = {"weapon": "Abyssal whip"}
monster = {"monsterId":"yama#normal"}

config  = {"monsterId":"yama#normal","setup":{"equipment":{"weapon":"abyssal whip"}}}
x = requests.post(dps_endpoint, json = config)
print(x.text)


VALID_PRAYERS = [
  BURST_OF_STRENGTH,
  CLARITY_OF_THOUGHT,
  SHARP_EYE,
  MYSTIC_WILL,
  SUPERHUMAN_STRENGTH,
  IMPROVED_REFLEXES,
  HAWK_EYE,
  MYSTIC_LORE,
  ULTIMATE_STRENGTH,
  INCREDIBLE_REFLEXES,
  EAGLE_EYE,
  MYSTIC_MIGHT,
  CHIVALRY,
  PIETY,
  RIGOUR,
  AUGURY,
  THICK_SKIN,
  ROCK_SKIN,
  STEEL_SKIN,
  DEADEYE,
  MYSTIC_VIGOUR,
]



class Equipment(BaseModel):
    ammo: str,
    body: str,
    cape: str,
    feet: str,
    hands: str,
    head: str,
    legs: str,
    neck: str,
    ring: str,
    shield: str,
    weapon: str,


class Skills(BaseModel):
    atk: int,
    def_: int = Field(alias="def")
    hp: int,
    magic: int,
    prayer: int,
    ranged: int,
    str_: int = Field(alias="str")
    mining: int,
    herblore: int,

class Boosts(BaseModel):
    atk: int,
    def_: int = Field(alias="def")
    hp: int,
    magic: int,
    prayer: int,
    ranged: int,
    str_: int = Field(alias="str")
    mining: int,
    herblore: int,

class Prayers(BaseModel):
    prayer: List[str]


