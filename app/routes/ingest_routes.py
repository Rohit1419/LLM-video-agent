from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.schemas.ingest_schema import VideoIngestRequest, VideoIngestResponse
from app.controllers import ingest_controller


router = APIRouter(prefix = "/api/v1/ingest" , tags = ["Ingestion"])

@router.post("/video", response_model=VideoIngestResponse)
def upload_video_transcript(
    request: VideoIngestRequest,
    # We require the API Key to be in the Header named 'x-api-key'
    x_api_key: str = Header(..., description="Tenant API Key for authentication"),
    db: Session = Depends(get_db)
):
    # upload or update the video transcript
    return ingest_controller.ingest_video_logic(db, request, x_api_key)


