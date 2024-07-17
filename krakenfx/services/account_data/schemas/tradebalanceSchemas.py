from typing import List, Optional

from pydantic import BaseModel


class SchemasTradeBalance(BaseModel):
    eb: str  # Equivalent balance (combined balance of all currencies)
    tb: str  # Trade balance (combined balance of all equity currencies)
    m: str  # Margin amount of open positions
    uv: str  # Unrealized value of open positions
    n: str  # Unrealized net profit/loss of open positions
    c: str  # Cost basis of open positions
    v: str  # Current floating valuation of open positions
    e: str  # Equity
    mf: str  # Free margin
    ml: Optional[str] = None  # Margin level

    model_config = {"from_attributes": True}


class SchemasTradeBalanceResponse(BaseModel):
    error: List[str]
    result: SchemasTradeBalance
