from fastapi import APIRouter, Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession
from app.config.database import get_db
from app.schemas.chat_schema import ChatRequest, ChatResponse
from app.controllers import chat_controller


router = APIRouter(prefix="/api/v1/chat", tags=["Chat"])


@router.post("/video", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
    x_api_key: str = Header(...),
):
    return await chat_controller.chat_with_video(db, request, x_api_key)
