from typing import Dict, List

from pydantic import BaseModel


class OHLCData(BaseModel):
    time: int
    open: float
    high: float
    low: float
    close: float
    vwap: float
    volume: float
    count: int


class OHLCResult(BaseModel):
    data: Dict[str, List[OHLCData]]
    last: int


class OHLCResponse(BaseModel):
    error: List[str]
    result: OHLCResult
