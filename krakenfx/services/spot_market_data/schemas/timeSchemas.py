from typing import List

from pydantic import BaseModel


class SchemasTime(BaseModel):
    unixtime: int
    rfc1123: str


class SchemasTimeResponse(BaseModel):
    error: List[str]
    result: SchemasTime
