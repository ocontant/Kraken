from typing import List, Optional
from pydantic import BaseModel, Field

class SchemasOpenOrderDescription(BaseModel):
    pair: str
    type: str
    ordertype: str
    price: str
    price2: str
    leverage: str
    order: str
    close: str

    model_config = {
        'from_attributes': True
    }

class SchemasOpenOrder(BaseModel):
    refid: Optional[str]
    userref: Optional[str]
    status: str
    opentm: float
    starttm: float
    expiretm: float
    descr: SchemasOpenOrderDescription
    vol: str
    vol_exec: str
    cost: str
    fee: str
    price: str
    stopprice: str
    limitprice: str
    misc: str
    oflags: str
    trades: Optional[List[str]] = []

    model_config = {
        'from_attributes': True
    }

class SchemasOpenOrdersResult(BaseModel):
    open: dict[str, SchemasOpenOrder]

    model_config = {
        'from_attributes': True
    }

class SchemasOpenOrdersResponse(BaseModel):
    error: List[str]
    result: SchemasOpenOrdersResult
