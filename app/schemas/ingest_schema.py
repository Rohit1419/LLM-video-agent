from pydantic import BaseModel
from typing import Dict, Any


# Request Schema(comming from client to ingest video transcript)
class VideoIngestRequest(BaseModel):
    video_id: str
    title: str
    transcript: str
    meta_data: Dict[str, Any] = {}


# Reasponse Schema
class VideoIngestResponse(BaseModel):
    video_id: str
    status: str
    message: str
