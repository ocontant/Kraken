from typing import List, Dict, Optional
from datetime import datetime
from pydantic import BaseModel, model_validator, ValidationError, Field

class SchemasOrderDescription(BaseModel):
    pair: str
    type: str
    ordertype: str
    price: str
    price2: str
    leverage: Optional[str] = None
    order: str
    close: Optional[str] = None

    model_config = {
        'from_attributes': True
    }

class SchemasOrder(BaseModel):
    refid: Optional[int] = None
    userref: Optional[int] = None
    status: str
    opentm: float
    closetm: Optional[float] = None #+
    starttm: Optional[float] = None
    expiretm: Optional[float] = None
    descr: SchemasOrderDescription
    vol: str
    vol_exec: str
    cost: str
    fee: str
    price: str
    stopprice: str
    limitprice: str
    misc: Optional[str]
    oflags: str
    margin: Optional[bool] = None #+
    trades: Optional[List[str]] = Field(default_factory=list)
    reason: Optional[str] = None #+

    model_config = {
        'from_attributes': True
    }

class SchemasOrdersResult(BaseModel):
    orders: Dict[str, SchemasOrder]

class SchemasOrdersResult(BaseModel):
    open: Optional[Dict[str, SchemasOrder]] = None
    closed: Optional[Dict[str, SchemasOrder]] = None
    count: Optional[int] = None

    model_config = {
        'extra': 'forbid'
    }

    @model_validator(mode='before')
    @classmethod
    def check_one_or_the_other(cls, values):
        open_orders = values.get('open')
        closed_orders = values.get('closed')
        if open_orders and closed_orders:
            raise ValueError('Only one of open or closed should be provided, not both.')
        if not open_orders and not closed_orders:
            raise ValueError('One of open or closed must be provided.')
        return values

class SchemasQueryOrdersResponse(BaseModel):
    result: Dict[str, SchemasOrder]

class SchemasOrdersResponse(BaseModel):
    error: List[str]
    result: SchemasOrdersResult