from typing import Any, Literal

import requests
from pydantic import BaseModel, Field


SkillName = Literal[
    "attack",
    "defence",
    "hitpoints",
    "magic",
    "prayer",
    "ranged",
    "strength",
    "mining",
    "herblore",
]

GearValue = int | str | None


class Stats(BaseModel):
    attack: int | None = None
    defence: int | None = None
    hitpoints: int | None = None
    magic: int | None = None
    prayer: int | None = None
    ranged: int | None = None
    strength: int | None = None
    mining: int | None = None
    herblore: int | None = None


class GearSlots(BaseModel):
    head: GearValue = None
    cape: GearValue = None
    neck: GearValue = None
    ammo: GearValue = None
    weapon: GearValue = None
    body: GearValue = None
    shield: GearValue = None
    legs: GearValue = None
    hands: GearValue = None
    feet: GearValue = None
    ring: GearValue = None

    def __truediv__(self, other: "GearSlots") -> "GearSlots":
        if not isinstance(other, GearSlots):
            return NotImplemented

        merged = self.model_dump()
        for slot, value in other.model_dump().items():
            if value is not None:
                merged[slot] = value
        return GearSlots.model_validate(merged)


class TtkSimpleRequest(BaseModel):
    boss: int | str
    gear: list[GearValue] | GearSlots
    prayer: str | None = None
    stats: Stats | None = None
    pot: str | None = None
    style: str | None = None
    debug: bool | None = None


class TtkSimpleResponse(BaseModel):
    ttk: float | None
    dps: float
    debug: dict[str, Any] | None = None


"""
$ curl -sS -X POST http://127.0.0.1:3000/osrs-dps/api/ttk \
  -H 'Content-Type: application/json' \
  -d '{"monsterId":"yama#normal","setup":{"equipment":{"weapon":"abyssal whip"}}}'
{"ttk":5449.774209796954,"dps":0.4601367138303325,"maxHit":24,"accuracy":0.09172160408578055,"attackSpeed":4,"monster":{"id":14176,"name":"Yama","version":"Normal","currentHp":2500}}
"""

DPS_ENDPOINT = "http://127.0.0.1:3001/osrs-dps/api/ttk-simple"


def fetch_ttk(payload: TtkSimpleRequest) -> TtkSimpleResponse:
    response = requests.post(
        DPS_ENDPOINT,
        json=payload.model_dump(exclude_none=True),
        timeout=30,
    )
    if not response.ok:
        try:
            detail = response.json()
        except Exception:
            detail = response.text
        raise RuntimeError(f"DPS API {response.status_code}: {detail}")
    return TtkSimpleResponse.model_validate(response.json())





def sequence_boss_pair(equip1: GearSlots, equip2: GearSlots, temp1, temp2):
    # TODO: abstract 
    pass




def main() -> None:
    base = {
        "stats": Stats(attack=99, strength=99, defence=99),
        "prayer": "Piety",
        "pot": "super_combat",
    }
    gear = GearSlots( # starting gear assumptions
        head="helm of neitiznot",
        neck="amulet of rancour",
        cape="Infernal cape",
        ammo="rada's blessing 4",
        shield="dragon defender",
        hands="ferocious gloves",
        body="fighter torso",
        legs="dragon platelegs",
        feet="Avernic treads (max)",
        ring="berserker ring (i)"
    )
    yama_unlocks = GearSlots(
        head="oathplate helm",
        body="oathplate chest",
        legs="oathplate legs"
    )
    vardorvis_unlocks = GearSlots(
        ring="ultor ring"       
    )
    
    # yama -> vardorvis routing
    yama_first_cttk = 0 # cumulative ttk
    yama_first_gear_0 = gear / GearSlots(weapon="emberlight")
    yama_first_in_0 = TtkSimpleRequest(
        boss="yama#normal",
        gear=yama_first_gear_0,
        style="slash",
        **base,
    )
    yama_first_res_0 = fetch_ttk(yama_first_in_0)
    yama_first_ttk_0 = yama_first_res_0.ttk
    yama_first_cttk += yama_first_ttk_0 * 1300 / 2 # expected kc for completion in duo, and also assume partner contributing equally.
    
    yama_first_gear_1 = gear / yama_unlocks / GearSlots(weapon="abyssal tentacle")
    yama_first_in_1 = TtkSimpleRequest(
        boss="vardorvis#post-quest",
        gear=yama_first_gear_1,
        style="lash",
        **base,
    )
    yama_first_res_1 = fetch_ttk(yama_first_in_1)
    yama_first_ttk_1 = yama_first_res_1.ttk
    yama_first_cttk += yama_first_ttk_1*1088
    print("yama first total ttk:", yama_first_cttk)

    # vardorvis -> yama routing
    vardorvis_first_cttk = 0
    vardorvis_first_gear_0 = gear /  GearSlots(weapon="abyssal tentacle")
    vardorvis_first_in_0 = TtkSimpleRequest(
        boss="vardorvis#post-quest",
        gear=vardorvis_first_gear_0,
        style="lash",
        **base,
    )
    vardorvis_first_res_0 = fetch_ttk(vardorvis_first_in_0)
    vardorvis_first_ttk_0 = vardorvis_first_res_0.ttk
    vardorvis_first_cttk += vardorvis_first_ttk_0 * 1088

    vardorvis_first_gear_1 = gear / vardorvis_unlocks / GearSlots(weapon="emberlight")
    vardorvis_first_in_1 = TtkSimpleRequest(
        boss="yama#normal",
        gear=vardorvis_first_gear_1,
        style="slash",
        **base,
    )
    vardorvis_first_res_1 = fetch_ttk(vardorvis_first_in_1)
    vardorvis_first_ttk_1 = vardorvis_first_res_1.ttk
    vardorvis_first_cttk += vardorvis_first_ttk_1 * 1300 / 2 # expected kc for completion in duo, and also assume partner contributing equally.
    
    print("Vardorvis first total ttk:", vardorvis_first_cttk)
    
    diff = abs(vardorvis_first_cttk - yama_first_cttk )
    
    print("diff: ", diff / 3600, "hrs")

if __name__ == "__main__":
    main()
