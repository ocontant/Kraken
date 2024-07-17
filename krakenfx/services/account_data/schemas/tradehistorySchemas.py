# krakenfx/api/schemas/trade_history.py
from typing import Dict, List, Optional

from pydantic import BaseModel


class SchemasTradeInfo(BaseModel):
    trade_id: int  # Unique identifier of trade executed
    ordertxid: str  # Order responsible for execution of trade
    postxid: str  # Position responsible for execution of trade
    pair: str  # Asset pair
    time: float  # Unix timestamp of trade
    type: str  # Type of order (buy/sell)
    ordertype: str  # Order type
    price: str  # Average price order was executed at (quote currency)
    cost: str  # Total cost of order (quote currency)
    fee: str  # Total fee (quote currency)
    vol: str  # Volume (base currency)
    margin: str  # Initial margin (quote currency)
    leverage: Optional[str] = None  # Amount of leverage used in trade
    misc: Optional[str] = (
        None  # Comma delimited list of miscellaneous info: closing — Trade closes all or part of a position
    )
    maker: bool  # true if trade was executed with user as the maker; false if taker
    posstatus: Optional[str] = (
        None  # Position status (open/closed) (Only present if trade opened a position)
    )
    cprice: Optional[float] = (
        None  # Average price of closed portion of position (quote currency)  (Only present if trade opened a position)
    )
    ccost: Optional[float] = (
        None  # Total cost of closed portion of position (quote currency) (Only present if trade opened a position)
    )
    cfee: Optional[float] = (
        None  # Total fee of closed portion of position (quote currency)  (Only present if trade opened a position)
    )
    cvol: Optional[float] = (
        None  # Total fee of closed portion of position (quote currency) (Only present if trade opened a position)
    )
    cmargin: Optional[float] = (
        None  # Total margin freed in closed portion of position (quote currency) (Only present if trade opened a position)
    )
    net: Optional[float] = (
        None  # Net profit/loss of closed portion of position (quote currency, quote currency scale) (Only present if trade opened a position)
    )
    trades: Optional[List[str]] = (
        None  # List of closing trades for position (if available) (Only present if trade opened a position)
    )

    model_config = {"from_attributes": True}


class SchemasTradesReturn(BaseModel):
    trades: Dict[str, SchemasTradeInfo]


class SchemasTradeHistoryResult(BaseModel):
    count: Optional[int] = None
    trades: Dict[str, SchemasTradeInfo]


class SchemasQueryTradesResponse(BaseModel):
    result: Dict[str, SchemasTradeInfo]


class SchemasTradeHistoryResponse(BaseModel):
    error: List[str]
    result: SchemasTradeHistoryResult
