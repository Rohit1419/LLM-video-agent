from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status
from app.models.core_models import Video, Tenant
from app.schemas.ingest_schema import VideoIngestRequest
from sqlalchemy.exc import IntegrityError, SQLAlchemyError


async def ingest_video_logic(
    db: AsyncSession, request: VideoIngestRequest, api_key: str
):
    try:
        # validate teh api key
        tenant = (
            (await db.execute(select(Tenant).where(Tenant.api_key == api_key)))
            .scalars()
            .first()
        )

        if not tenant:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API Key. You are not authorized to perform this action.",
            )

        # checking if video already exists
        existing_video = (
            (
                await db.execute(
                    select(Video).where(
                        Video.id == request.video_id, Video.tenant_id == tenant.id
                    )
                )
            )
            .scalars()
            .first()
        )

        if existing_video:
            # update the existing video
            existing_video.title = request.title
            existing_video.transcript_text = request.transcript
            existing_video.meta_data = request.meta_data

            await db.commit()
            return {
                "video_id": request.video_id,
                "status": "updated",
                "message": f"Video '{request.title}' updated successfully.",
            }

        else:
            # create a new video
            new_video = Video(
                id=request.video_id,
                tenant_id=tenant.id,
                title=request.title,
                transcript_text=request.transcript,
                meta_data=request.meta_data,
            )

            db.add(new_video)
            await db.commit()
            await db.refresh(new_video)

            return {
                "video_id": new_video.id,
                "status": "created",
                "message": f"Video '{request.title}' ingested successfully.",
            }

    except IntegrityError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Database integrity error: Video ID might already exist or violates constraints: {str(e)}",
        )

    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error occurred: {str(e)}",
        )

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}",
        )
