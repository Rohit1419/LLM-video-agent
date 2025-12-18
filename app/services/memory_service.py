import json
from app.config.redis_client import redis_client

SESSION_TTL = 3600  # expirey after 1 hr


class MemoryService:
    @staticmethod
    async def get_history(session_id: str):
        history_json = await redis_client.lrange(f"chat:{session_id}", 0, -1)

        # Converts the  ["{'role': 'user'..}", ..] back to Dicts
        return [json.loads(msg) for msg in history_json]

    @staticmethod
    async def add_message(session_id: str, role: str, content: str):
        message = json.dumps({"role": role, "content": content})

        await redis_client.rpush(f"chat:{session_id}", message)

        await redis_client.expire(f"chat:{session_id}", SESSION_TTL)
