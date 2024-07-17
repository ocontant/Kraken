from typing import Dict, List

from pydantic import BaseModel


class SchemasAssets(BaseModel):
    aclass: str
    altname: str
    decimals: int
    display_decimals: int
    status: str


class SchemasAssetsReturn(BaseModel):
    assets: Dict[str, SchemasAssets]


class SchemasResponse(BaseModel):
    error: List[str]
    result: Dict[str, SchemasAssets]
