from typing import Any, Dict, List, Union

from pydantic import BaseModel, field_validator


class SchemasSpread(BaseModel):
    timestamp: int
    bid: str
    ask: str


class SchemasGetRecentSpreadsResponse(BaseModel):
    error: List[str]
    result: Dict[str, Union[List[SchemasSpread], int]]

    @field_validator("result", mode="before")
    @classmethod
    def parse_result(cls, value: Any):
        if isinstance(value, dict):
            parsed_result = {}
            for key, spreads in value.items():
                if key == "last":
                    parsed_result[key] = spreads
                else:
                    if not isinstance(spreads, list):
                        raise TypeError(
                            f"Expected list for spreads, got {type(spreads)}"
                        )
                    for spread in spreads:
                        if not isinstance(spread, list) or len(spread) != 3:
                            raise TypeError(
                                f"Expected list of length 3 for each spread, got {spread}"
                            )
                    parsed_result[key] = [
                        SchemasSpread(timestamp=spread[0], bid=spread[1], ask=spread[2])
                        for spread in spreads
                    ]
            return parsed_result
        raise TypeError(f"Expected dict for result, got {type(value)}")

    class Config:
        allow_population_by_field_name = True
