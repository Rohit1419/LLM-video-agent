from pydantic import BaseModel
from typing import Optional


class ChatRequest(BaseModel):
    video_id: str
    session_id: str
    user_query: str
    model: Optional[str] = "openai/gpt-oss-120b:free"


class ChatResponse(BaseModel):
    answer: str
