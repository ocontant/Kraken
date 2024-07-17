from typing import Any, Dict, List

from pydantic import BaseModel, model_validator


class SchemasTradeEntry(BaseModel):
    price: str
    volume: str
    time: float
    type: str
    order_type: str
    miscellaneous: str
    trade_id: int


class SchemasRecentTradesResponse(BaseModel):
    error: List[str]
    result: Dict[str, List[SchemasTradeEntry]]

    @model_validator(mode="before")
    def transform_trades(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        if "result" not in values:
            raise ValueError("'result' key not found in the response")

        result = values["result"]
        parsed_result = {
            pair: [
                {
                    "price": trade[0],
                    "volume": trade[1],
                    "time": trade[2],
                    "type": trade[3],
                    "order_type": trade[4],
                    "miscellaneous": trade[5],
                    "trade_id": trade[6],
                }
                for trade in trades_data
            ]
            for pair, trades_data in result.items()
            if pair != "last"
        }
        values["result"] = parsed_result
        return values

    @classmethod
    def from_response(cls, response: dict):
        return cls.model_validate(response)
