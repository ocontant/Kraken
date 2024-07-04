from pydantic import BaseModel
from typing import List

class SchemasTime(BaseModel):
    unixtime: int
    rfc1123: str

class SchemasTimeResponse(BaseModel):
    error: List[str]
    result: SchemasTime