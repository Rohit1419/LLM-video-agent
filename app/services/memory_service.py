import json
from app.config.redis_client import redis_client

SESSION_TTL = 3600  # expirey after 1 hr


class MemoryService:
    @staticmethod
    async def get_history(tenant_id: str, session_id: str):
        # now combining the tenant_id with session_id, which will not brake under same
        #  session id
        key = f"chat:{tenant_id}:{session_id}"
        history_json = await redis_client.lrange(key, 0, -1)

        # Converts the  ["{'role': 'user'..}", ..] back to Dicts
        return [json.loads(msg) for msg in history_json]

    @staticmethod
    async def add_message(tenant_id: str, session_id: str, role: str, content: str):
        key = f"chat:{tenant_id}:{session_id}"
        message = json.dumps({"role": role, "content": content})

        await redis_client.rpush(key, message)

        await redis_client.expire(key, SESSION_TTL)
