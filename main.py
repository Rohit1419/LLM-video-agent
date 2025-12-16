from fastapi import FastAPI
from app.config.database import engine, Base
from app.routes import ingest_routes
from contextlib import asynccontextmanager


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


@app.get("/")
def health_check():
    return {
        "status": "active",
        "service": "Video Chat LLM agent is running.",
        "version": "1.0.0",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
