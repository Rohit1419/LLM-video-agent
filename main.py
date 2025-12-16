from fastapi import FastAPI
from dotenv import load_dotenv

# load env variables from .env file
load_dotenv()

app = FastAPI(
    title = "Video Chat LLM agent",
    description = "A FastAPI application for video interaction with LLM agents.",
    version = "1.0.0"
)


@app.get("/")
def health_check():
    return {"status": "ok",
            "service": "Video Chat LLM agent is running.",
            "version": "1.0.0"
            }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host= "0.0.0.0", port =8000, reload=True)
