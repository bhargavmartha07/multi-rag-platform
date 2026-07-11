from pydantic import BaseModel


class QueryRequest(BaseModel):

    query: str


class SourceDocument(BaseModel):

    document_id: int
    content: str


class QueryResponse(BaseModel):

    answer: str
    sources: list[SourceDocument]
