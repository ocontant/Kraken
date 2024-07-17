# depthSchemas.py
from typing import Any, Dict, List

from pydantic import BaseModel, model_validator


class ModelOrder(BaseModel):
    price: str
    volume: str
    timestamp: int


class ModelAssetPair(BaseModel):
    asks: List[ModelOrder]
    bids: List[ModelOrder]

    @model_validator(mode="before")
    @classmethod
    def parse_orders(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        if "asks" in values:
            values["asks"] = [
                ModelOrder(price=o[0], volume=o[1], timestamp=o[2])
                for o in values["asks"]
            ]
        if "bids" in values:
            values["bids"] = [
                ModelOrder(price=o[0], volume=o[1], timestamp=o[2])
                for o in values["bids"]
            ]
        return values


class ModelResponseSchema(BaseModel):
    error: List[str]
    result: Dict[str, ModelAssetPair]

    @model_validator(mode="before")
    @classmethod
    def parse_asset_pairs(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        if "result" in values:
            values["result"] = {
                k: ModelAssetPair(**v) for k, v in values["result"].items()
            }
        return values
