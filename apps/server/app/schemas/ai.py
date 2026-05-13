from pydantic import BaseModel


class ChatRequest(BaseModel):
    question: str
    session_id: str | None = None


class SourceCitation(BaseModel):
    post_id: str
    post_title: str
    post_slug: str
    chunk_text: str


class ChatResponse(BaseModel):
    answer: str
    sources: list[SourceCitation] = []
    session_id: str
