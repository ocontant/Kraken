from pydantic import BaseModel
from typing import List, Dict


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
