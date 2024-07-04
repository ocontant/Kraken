from pydantic import BaseModel, Field, model_validator
from typing import List, Dict, Union, Optional

class SchemasFeeSchedule(BaseModel):
    volume: int
    fee: float

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

SchemasResultType = Union[SchemasAssetPairDetails, SchemasCollateralAssetDetails]

class SchemasReturnAssetPair(BaseModel):
    asset_pairs: Dict[str, SchemasResultType]

    @model_validator(mode='before')
    @classmethod
    def check_result(cls, values):
        asset_pairs = values.get('asset_pairs', {})
        for key, value in asset_pairs.items():
            if 'aclass_base' in value:
                asset_pairs[key] = SchemasAssetPairDetails.from_dict(value)
            elif 'aclass' in value:
                asset_pairs[key] = SchemasCollateralAssetDetails(**value)
            else:
                raise ValueError(f"Unknown structure for asset pair: {key}")
        values['asset_pairs'] = asset_pairs
        return values

    @classmethod
    def from_dict(cls, dct: Dict):
        return cls(asset_pairs=dct['asset_pairs'])
    

class SchemasReturnCollateralAssetDetails(BaseModel):
    assets: Dict[str, SchemasCollateralAssetDetails]

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
