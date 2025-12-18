from pydantic import BaseModel
from typing import Optional


class ChatRequest(BaseModel):
    video_id: str
    session_id: str
    user_query: str
    model: Optional[str] = "gemini/gemini-2.5-flash-lite"


class ChatResponse(BaseModel):
    answer: str
