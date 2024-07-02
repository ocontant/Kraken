from pydantic import BaseModel, Field, model_validator
from typing import List, Dict, Union, Optional
from krakenfx.api.models.assetsPairsModel import (
    ModelFeeSchedule as ORMFeeSchedule,
    ModelAssetPairDetails as ORMAssetPairDetails,
    ModelCollateralAssetDetails as ORMCollateralAssetDetails
)

class SchemasFeeSchedule(BaseModel):
    volume: int
    fee: float

    class Meta:
        orm_model = ORMFeeSchedule

    @classmethod
    def from_list(cls, lst: List):
        return cls(volume=lst[0], fee=lst[1])

class SchemasAssetPairDetails(BaseModel):
    altname: str
    wsname: str
    aclass_base: str
    base: str
    aclass_quote: str
    quote: str
    lot: str
    cost_decimals: int
    pair_decimals: int
    lot_decimals: int
    lot_multiplier: int
    leverage_buy: List[int]
    leverage_sell: List[int]
    fees: List[SchemasFeeSchedule]
    fees_maker: List[SchemasFeeSchedule]
    fee_volume_currency: str
    margin_call: int
    margin_stop: int
    ordermin: str
    costmin: str
    tick_size: str
    status: str
    long_position_limit: Optional[int] = None
    short_position_limit: Optional[int] = None

    class Meta:
        orm_model = ORMAssetPairDetails

    @classmethod
    def from_dict(cls, dct: Dict):
        dct['fees'] = [SchemasFeeSchedule.from_list(fee) for fee in dct['fees']]
        dct['fees_maker'] = [SchemasFeeSchedule.from_list(fee) for fee in dct['fees_maker']]
        return cls(**dct)

class SchemasCollateralAssetDetails(BaseModel):
    aclass: str
    altname: str
    decimals: int
    display_decimals: int
    collateral_value: Optional[float] = None
    status: str

    class Meta:
        orm_model = ORMCollateralAssetDetails

SchemasResultType = Union[SchemasAssetPairDetails, SchemasCollateralAssetDetails]

class SchemasResponse(BaseModel):
    error: List[str]
    result: Dict[str, SchemasResultType]

    @model_validator(mode='before')
    def check_result(cls, values):
        result = values.get('result', {})
        for key, value in result.items():
            if 'aclass_base' in value:
                result[key] = SchemasAssetPairDetails.from_dict(value)
            elif 'aclass' in value:
                result[key] = SchemasCollateralAssetDetails(**value)
            else:
                raise ValueError(f"Unknown structure for result key: {key}")
        values['result'] = result
        return values

    @classmethod
    def from_dict(cls, dct: Dict):
        return cls(error=dct['error'], result=dct['result'])
