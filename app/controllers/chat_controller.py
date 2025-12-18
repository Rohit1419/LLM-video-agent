from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status
from litellm import acompletion
from litellm.exceptions import RateLimitError
from app.models.core_models import Video, Tenant
from app.schemas.chat_schema import ChatRequest
import os
from app.services.memory_service import MemoryService

SYSTEM_PROMPT_TEMPLATE = """
You are a helpful teaching assistant for a video course.
You are provided with the FULL TRANSCRIPT of the video below.


INSTRUCTIONS:

1. you are assistence to know about the user and keep remember the previous chats
2. you have to remember the user basic personal information, like name, age, etc. 
4. always keep the answer as concise as possible
TRANSCRIPT:
{transcript_text}
"""


async def chat_with_video(db: AsyncSession, request: ChatRequest, api_key: str):
    # verfiy the client and video for the request
    tenant = (
        (await db.execute(select(Tenant).where(Tenant.api_key == api_key)))
        .scalars()
        .first()
    )

    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key.",
        )

    video = (
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

    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found",
        )

    history = await MemoryService.get_history(
        tenant_id=tenant.id, session_id=request.session_id
    )
    print("Chat history:", history)

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT_TEMPLATE.format(
                transcript_text=video.transcript_text
            ),
        }
    ]

    messages.extend(history)

    messages.append({"role": "user", "content": request.user_query})

    # LLM call

    try:
        response = await acompletion(
            model=request.model,
            messages=messages,
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url="https://openrouter.ai/api/v1",
        )

        answer_text = response.choices[0].message.content

        # saving to redis memory
        # 1. user query
        await MemoryService.add_message(
            tenant_id=tenant.id,
            session_id=request.session_id,
            role="user",
            content=request.user_query,
        )

        # 2. LLM answer
        await MemoryService.add_message(
            tenant_id=tenant.id,
            session_id=request.session_id,
            role="assistant",
            content=answer_text,
        )

        return {"answer": answer_text}

    except RateLimitError:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="AI quota exceeded. Please try again later.",
        )

    except Exception as e:
        print(f"Error during LLM call: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error during the request with the ai model.",
        )
