from typing import List

from pydantic import BaseModel


class SchemasStatus(BaseModel):
    status: str
    timestamp: str


class SchemasResponse(BaseModel):
    error: List[str]
    result: SchemasStatus
