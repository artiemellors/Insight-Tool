"""Insight Tool — FastAPI application entry point."""

from fastapi import FastAPI

from app.api.routes import router

app = FastAPI(
    title="Insight Tool",
    description="AI-assisted analysis of customer interview transcripts",
    version="0.1.0",
)

app.include_router(router)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}
