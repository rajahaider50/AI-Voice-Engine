import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .api.tts_routes import router as tts_router
from .core.config import OUTPUT_DIR

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

app = FastAPI(
    title="AI Voice Engine",
    description="Text-to-Speech API with multiple voices and emotions",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/audio", StaticFiles(directory=str(OUTPUT_DIR)), name="audio")

app.include_router(tts_router, prefix="/api/v1")


@app.get("/")
async def root():
    return {
        "name": "AI Voice Engine",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "tts": "/api/v1/tts",
            "voices": "/api/v1/voices",
            "health": "/api/v1/health",
        },
    }
