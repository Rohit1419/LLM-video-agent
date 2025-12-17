from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status
from litellm import acompletion
from app.models.core_models import Video, Tenant
from app.schemas.chat_schema import ChatRequest
import os

SYSTEM_PROMPT_TEMPLATE = """
You are a helpful teaching assistant for a video course.
You are provided with the FULL TRANSCRIPT of the video below.

CONTEXT:
- Current Student query : {user_query}

INSTRUCTIONS:
1. Answer the student's question based ONLY on the provided transcript.
2. If the question is about the current scene, prioritize the text around 
3. If the answer is not in the video, say "I cannot find that information in this video."
4. Be concise and encouraging.

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

    # final system prompt
    final_system_prompt = SYSTEM_PROMPT_TEMPLATE.format(
        transcript_text=video.transcript_text,
        user_query=request.user_query,
    )

    messages = [
        {"role": "system", "content": final_system_prompt},
        {"role": "user", "content": request.user_query},
    ]

    # LLM call

    try:
        response = await acompletion(
            model=request.model, messages=messages, api_key=os.getenv("GEMINI_API_KEY")
        )

        answer_text = response.choices[0].message.content
        return {"answer": answer_text}

    except Exception as e:
        print(f"Error during LLM call: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error during the request with the ai model.",
        )
