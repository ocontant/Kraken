# krakenfx/api/schemas/openPositionSchemas.py
from typing import Dict, List, Optional, Union

from pydantic import BaseModel, field_validator


class SchemasOpenPosition(BaseModel):
    ordertxid: str  # Transaction ID of the order responsible for the position.
    posstatus: str  # Position status.
    pair: str  # Asset pair.
    time: float  # Unix timestamp of the position opening time.
    type: str  # Type of order used to open the position (buy/sell).
    ordertype: str  # Order type used to open the position.
    cost: str  # Opening cost of the position.
    fee: str  # Opening fee of the position.
    vol: str  # Volume of the position (base currency).
    vol_closed: str  # Volume of the position that has been closed (base currency).
    margin: str  # Initial margin level of the position.
    terms: str  # Terms of the position.
    rollovertm: str  # Rollover time.
    value: Optional[str] = None  # Current value of the position (optional).
    net: Optional[str] = None  # Unrealized profit/loss of the position (optional).
    misc: str  # Miscellaneous information about the position.
    oflags: str  # Order flags for the position.

    model_config = {"from_attributes": True}

    def to_json(self):
        return {
            "ordertxid": self.ordertxid,
            "posstatus": self.posstatus,
            "pair": self.pair,
            "time": self.time,
            "type": self.type,
            "ordertype": self.ordertype,
            "cost": self.cost,
            "fee": self.fee,
            "vol": self.vol,
            "vol_closed": self.vol_closed,
            "margin": self.margin,
            "terms": self.terms,
            "rollovertm": self.rollovertm,
            "value": self.value,
            "net": self.net,
            "misc": self.misc,
            "oflags": self.oflags,
        }


class SchemasConsolidatedOpenPosition(BaseModel):
    pair: str  # Asset pair.
    positions: str  # Number of positions.
    type: str  # Type of order used to open the position (buy/sell).
    leverage: str  # Leverage used.
    cost: str  # Opening cost of the position.
    fee: str  # Opening fee of the position.
    vol: str  # Volume of the position (base currency).
    vol_closed: str  # Volume of the position that has been closed (base currency).
    margin: str  # Initial margin level of the position.
    value: str  # Current value of the position.
    net: str  # Unrealized profit/loss of the position.

    def to_json(self):
        return {
            "pair": self.pair,
            "positions": self.positions,
            "type": self.type,
            "leverage": self.leverage,
            "cost": self.cost,
            "fee": self.fee,
            "vol": self.vol,
            "vol_closed": self.vol_closed,
            "margin": self.margin,
            "value": self.value,
            "net": self.net,
        }


class SchemasOpenPositions(BaseModel):
    openPositions: Dict[str, SchemasOpenPosition]


class SchemasConsolidatedOpenPositions(BaseModel):
    consolidatedOpenPositions: List[SchemasConsolidatedOpenPosition]


class SchemasOpenPositionReturn(BaseModel):
    openPositions: SchemasOpenPositions
    consolidatedOpenPositions: SchemasConsolidatedOpenPositions


class SchemasOpenPositionResponse(BaseModel):
    error: List[str]  # List of errors returned by the API, if any.
    result: Union[
        Dict[str, SchemasOpenPosition], List[SchemasConsolidatedOpenPosition]
    ]  # Dictionary of open positions or list of consolidated open positions.

    @field_validator("result", mode="before")
    def validate_result(cls, v):
        if isinstance(v, dict):
            return v  # It's an individual positions response
        elif isinstance(v, list):
            if all(isinstance(item, dict) and "pair" in item for item in v):
                return v  # It's a consolidated positions response
        raise ValueError(
            "result must be a dictionary of OpenPosition objects or a list of ConsolidatedOpenPosition objects"
        )

    def to_json(self):
        result = self.result
        if isinstance(result, dict):
            return {"error": [], "result": [SchemasOpenPosition(**result)]}
        elif isinstance(result, list):
            consolidated_positions = [
                SchemasConsolidatedOpenPosition(**pos) for pos in result
            ]
            return {"error": [], "result": consolidated_positions}
