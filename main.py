from fastapi import FastAPI
from app.config.database import engine, Base
from app.routes import ingest_routes, chat_routes
from contextlib import asynccontextmanager
from app.models.core_models import Tenant
from sqlalchemy.ext.asyncio import AsyncSession
from app.config.database import get_db
from fastapi import Depends


# create all tables
@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    title="Video Chat LLM agent",
    description="A FastAPI application for video interaction with LLM agents.",
    version="1.0.0",
    lifespan=lifespan,
)

#  ingestion routes
app.include_router(ingest_routes.router)

# chat routes
app.include_router(chat_routes.router)


@app.get("/")
def health_check():
    return {
        "status": "active",
        "service": "Video Chat LLM agent is running.",
        "version": "1.0.0",
    }


@app.get("/create-test-tenant")
async def create_test_user(db: AsyncSession = Depends(get_db)):
    new_tenant = Tenant(name="Test User", api_key="test_key_123")
    db.add(new_tenant)
    try:
        await db.commit()
        return {"msg": "Created! Use API Key: test_key_123"}
    except Exception as e:
        await db.rollback()
        return {"msg": f"User already exists or error: {str(e)}"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
