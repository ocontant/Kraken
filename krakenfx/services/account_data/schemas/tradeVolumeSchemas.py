from typing import Dict, List, Optional

from pydantic import BaseModel


class SchemasFeesTaker(BaseModel):
    fee: str
    minfee: str
    maxfee: str
    nextfee: str
    tiervolume: str
    nextvolume: str


class SchemasFeesMaker(BaseModel):
    fee: str
    minfee: str
    maxfee: str
    nextfee: Optional[str] = None
    nextvolume: Optional[str] = None
    tiervolume: str


class SchemasVolumeSubaccount(BaseModel):
    iiban: str
    volume: str


class SchemasResult(BaseModel):
    currency: str
    volume: str
    volume_subaccounts: List[SchemasVolumeSubaccount]
    fees: Dict[str, SchemasFeesTaker]
    fees_maker: Dict[str, SchemasFeesMaker]


class SchemasResponse(BaseModel):
    error: List[str]
    result: SchemasResult
