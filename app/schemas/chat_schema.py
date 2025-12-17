from pydantic import BaseModel
from typing import Optional


class ChatRequest(BaseModel):
    video_id: str
    user_query: str
    timestamp: Optional[str] = "00:00"
    model: Optional[str] = "gemini/gemini-2.0-flash-lite"


class ChatResponse(BaseModel):
    answer: str
