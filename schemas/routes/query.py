
from pydantic import BaseModel


class QueryRequest(BaseModel):
    subject: str
    description: str
