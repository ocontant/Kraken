from pydantic import BaseModel, Field
from typing import List, Dict, Union

class TickerInfo(BaseModel):
    a: List[Union[str, float]] = Field(..., min_items=3, max_items=3)
    """Ask array. Contains the price, whole lot volume, and lot volume."""
    
    b: List[Union[str, float]] = Field(..., min_items=3, max_items=3)
    """Bid array. Contains the price, whole lot volume, and lot volume."""
    
    c: List[Union[str, float]] = Field(..., min_items=2, max_items=2)
    """Last trade closed array. Contains the price and lot volume."""
    
    v: List[Union[str, float]] = Field(..., min_items=2, max_items=2)
    """Volume array. Contains the volume today and volume over the last 24 hours."""
    
    p: List[Union[str, float]] = Field(..., min_items=2, max_items=2)
    """Volume weighted average price array. Contains the VWAP today and VWAP over the last 24 hours."""
    
    t: List[int] = Field(..., min_items=2, max_items=2)
    """Number of trades array. Contains the number of trades today and over the last 24 hours."""
    
    l: List[Union[str, float]] = Field(..., min_items=2, max_items=2)
    """Low price array. Contains the lowest price today and the lowest price over the last 24 hours."""
    
    h: List[Union[str, float]] = Field(..., min_items=2, max_items=2)
    """High price array. Contains the highest price today and the highest price over the last 24 hours."""
    
    o: Union[str, float]
    """Today's opening price."""

class TickerResult(BaseModel):
    error: List[str]
    result: Dict[str, TickerInfo]
    
