from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.core_models import Video, Tenant
from app.schemas.ingest_schema import VideoIngestRequest

def ingest_video_logic(db:Session,  request:VideoIngestRequest, api_key: str):

    # validate teh api key 
    tenant = db.query(Tenant).filter(Tenant.api_key == api_key).frist()

    if not tenant: 
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Invalid API Key. You are not authorized to perform this action."
        )

    # checking if video already exists 

    existing_video = db.query(Video).filter(Video.tenant_id == tenant.id, Video.tenant_id == request.video_id).first()

    if existing_video:
        # update the existing video 
        existing_video.title = request.title
        existing_video.transcript_text = request.transcript
        existing_video.meta_data = request.meta_data

        db.commit()
        return {
            "video_id" : request.video_id,
            "status" : "updated",
            "message": f"Video '{request.title}' updated successfully."
        }
    
    else:
        # create a new video 

        new_video = Video(
            id = request.video_id,
            tenant_id = tenant.id,
            title = request.title,
            transcript_text = request.transcript,
            meta_data = request.meta_data
        )

        db.add(new_video)
        db.commit()
        db.refresh(new_video)

        return{
            "video_id" : new_video.id,
            "status" : "created",
            "message": f"Video '{request.title}' ingested successfully."
        }

