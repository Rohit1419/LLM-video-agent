from fastapi import FastAPI
from app.config.database import engine, Base
from app.models import core_models
from app.routes import ingest_routes

# create all tables
Base.metadata.create_all(bind = engine)

app = FastAPI(
    title = "Video Chat LLM agent",
    description = "A FastAPI application for video interaction with LLM agents.",
    version = "1.0.0"
)

#  ingestion routes
app.include_router(ingest_routes.router)


@app.get("/")
def health_check():
    return {"status": "ok",
            "service": "Video Chat LLM agent is running.",
            "version": "1.0.0"
            }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host= "0.0.0.0", port =8000, reload=True)
