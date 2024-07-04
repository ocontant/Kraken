from pydantic import BaseModel
from typing import List

class SchemasStatus(BaseModel):
    status: str
    timestamp: str

class SchemasResponse(BaseModel):
    error: List[str]
    result: SchemasStatus