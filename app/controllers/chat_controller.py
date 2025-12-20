from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status
from litellm import acompletion
from litellm.exceptions import RateLimitError
from app.models.core_models import Video, Tenant
from app.schemas.chat_schema import ChatRequest
import os
from app.services.memory_service import MemoryService

import logging

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

SYSTEM_PROMPT_TEMPLATE = """
### ROLE
You are an expert Teaching Assistant for a video course. Your goal is to help students understand concepts by answering their questions clearly and accurately.

### INPUT DATA
You have access to the following Video Transcript:
<transcript>
{transcript_text}
</transcript>

### INSTRUCTIONS
1. **Analyze the Question:**
   - First, determine if the user's question is related to the course subject matter or the specific video content.
   - If the question is completely unrelated (e.g., asking about cooking in a coding course), politely refuse to answer.

2. **Source of Truth Priority:**
   - **Primary:** Use the information provided in the <transcript> to answer the question. Quote or reference specific parts if possible.
   - **Secondary:** If the transcript does not fully cover the answer, BUT the question is strictly related to the course subject, use your own internal knowledge to provide a complete answer.
   - **Constraint:** Do NOT use your internal knowledge to answer off-topic questions.

3. **Response Style:**
   - Be descriptive and educational. Explain *why* and *how*, don't just give a one-word answer.
   - Use formatting (bullet points, **bold text**, code blocks) to make the answer easy to read.
   - Tone: Encouraging, professional, and helpful.

### EXAMPLE INTERACTION

**Transcript Snippet:**
"...so when we want to change the UI in React, we can't just change the variable directly. We have to use a hook called useState. It returns two things: the current state value and a function to update it. By convention, we name them strictly, like const [count, setCount] = useState(0). If you try to say count = 5, React won't know, and the screen won't update..."

**Student Question:**
"Why do we use 'const' if the value is going to change? And can I name the second thing 'changeCount' instead of 'setCount'?"

**Your Thought Process:**
1. *Is this related?* Yes, strict React question.
2. *Is it in the transcript?*
   - Transcript says "we name them strictly" but doesn't explain *why* we use `const` for a changing value (this requires external knowledge).
   - Transcript mentions "by convention," but doesn't explicitly say if we *can* break the convention (needs clarification).
3. *Plan:* Explain `const` refers to the array reference (external knowledge) and clarify the naming convention (transcript + external knowledge).

**Your Response:**
"Great questions! Let's break this down based on the video and React principles.

**1. Why use `const`?**
Even though the *value* of the state changes (e.g., from 0 to 5), the *reference* to the variables `count` and `setCount` comes from a function call (`useState`) that runs every render.
* You use `const` because you should **never reassign the variable directly** (like `count = 5`). As the video mentions: _"If you try to say count = 5, React won't know."_ Using `const` prevents you from making this mistake.

**2. Can you name it 'changeCount'?**
Technically, **yes**.
The video says _"By convention, we name them strictly,"_ but this is just a best practice, not a rigid rule.
* `useState` returns an array, so you can destructure it with any names you want:
    ```javascript
    const [score, changeScore] = useState(0); // This works!
    ```
* **However**, the standard convention (using `set` + VariableName) makes your code much easier for others to read."
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
    # chat histroy logging
    logger.info(f"Retrieved {len(history)} messages for session {request.session_id}")

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
            api_key=os.getenv("GEMINI_API_KEY"),
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
        logger.error(f"LLM Failure for {request.video_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error during the request with the ai model.",
        )
