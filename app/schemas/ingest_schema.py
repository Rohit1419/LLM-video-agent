from pydantic import BaseModel
from typing import Optional, Dict, Any


# Request Schema(comming from client to ingest video transcript)
class VideoIngestRequest(BaseModel):
    video_id = str
    title : str
    transcript: str
    meta_data : Dict[str, Any] = {}  # Optional metadata about the video


#Reasponse Schema 
class VideoIngestResponse(BaseModel):
    video_id : str
    status : str
    message : str