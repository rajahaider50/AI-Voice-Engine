from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from pathlib import Path

from ..core.config import (
    TTSRequest, TTSResponse, HealthResponse,
    OUTPUT_DIR, VoiceGender, Language
)
from ..services.tts_pipeline import TTSPipeline

router = APIRouter()
pipeline = TTSPipeline()


@router.on_event("startup")
async def startup_event():
    pipeline.initialize()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        voices_loaded=len(pipeline.voice_library.list_voices()),
        models_loaded=1 if pipeline.tts_model.is_loaded else 0,
    )


@router.post("/tts", response_model=TTSResponse)
async def text_to_speech(request: TTSRequest):
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    if len(request.text) > 5000:
        raise HTTPException(status_code=400, detail="Text too long (max 5000 chars)")

    voice = pipeline.voice_library.get_voice(request.voice_id)
    if not voice:
        raise HTTPException(status_code=404, detail=f"Voice '{request.voice_id}' not found")

    result = pipeline.process(request)
    if not result:
        raise HTTPException(status_code=500, detail="TTS processing failed")

    return result


@router.get("/audio/{filename}")
async def get_audio(filename: str):
    filepath = OUTPUT_DIR / filename
    if not filepath.exists():
        raise HTTPException(status_code=404, detail="Audio file not found")

    return FileResponse(
        path=str(filepath),
        media_type="audio/wav",
        filename=filename,
    )


@router.get("/voices")
async def list_voices():
    voices = pipeline.voice_library.list_voices()
    return {
        "voices": [
            {
                "id": v.id,
                "name": v.name,
                "gender": v.gender.value,
                "style": v.style.value,
                "language": v.language.value,
            }
            for v in voices
        ],
        "total": len(voices),
    }


@router.get("/voices/{gender}")
async def list_voices_by_gender(gender: str):
    try:
        gender_enum = VoiceGender(gender)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid gender. Use 'male' or 'female'")

    voices = pipeline.voice_library.get_voices_by_gender(gender_enum)
    return {
        "voices": [
            {
                "id": v.id,
                "name": v.name,
                "style": v.style.value,
                "language": v.language.value,
            }
            for v in voices
        ],
        "total": len(voices),
    }


@router.get("/voices/language/{language}")
async def list_voices_by_language(language: str):
    try:
        lang_enum = Language(language)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid language code")

    voices = pipeline.voice_library.get_voices_by_language(lang_enum)
    return {
        "voices": [
            {
                "id": v.id,
                "name": v.name,
                "gender": v.gender.value,
                "style": v.style.value,
            }
            for v in voices
        ],
        "total": len(voices),
    }


@router.get("/history")
async def get_history():
    return {"history": pipeline.get_history()}


@router.get("/stats")
async def get_stats():
    return pipeline.get_stats()


@router.delete("/audio/{filename}")
async def delete_audio(filename: str):
    filepath = OUTPUT_DIR / filename
    if not filepath.exists():
        raise HTTPException(status_code=404, detail="Audio file not found")

    filepath.unlink()
    return {"message": f"Deleted {filename}"}
