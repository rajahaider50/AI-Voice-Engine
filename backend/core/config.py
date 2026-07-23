from pathlib import Path
from pydantic import BaseModel
from typing import Optional, List
from enum import Enum


class VoiceGender(str, Enum):
    FEMALE = "female"
    MALE = "male"


class VoiceStyle(str, Enum):
    SOFT = "soft"
    CALM = "calm"
    YOUNG = "young"
    PROFESSIONAL = "professional"
    EMOTIONAL = "emotional"
    DEEP = "deep"
    FRIENDLY = "friendly"


class EmotionType(str, Enum):
    NEUTRAL = "neutral"
    HAPPY = "happy"
    SAD = "sad"
    ANGRY = "angry"
    FEARFUL = "fearful"
    DISGUSTED = "disgusted"
    SURPRISED = "surprised"


class Language(str, Enum):
    ENGLISH = "en"
    URDU = "ur"
    HINDI = "hi"
    ARABIC = "ar"
    TURKISH = "tr"
    FRENCH = "fr"
    GERMAN = "de"
    SPANISH = "es"


class TTSRequest(BaseModel):
    text: str
    voice_id: str = "female1"
    speed: float = 1.0
    pitch: float = 1.0
    volume: float = 1.0
    emotion: EmotionType = EmotionType.NEUTRAL
    language: Language = Language.ENGLISH
    pause_control: float = 0.5
    breath_effect: bool = True
    speaking_style: str = "normal"


class TTSResponse(BaseModel):
    audio_url: str
    duration: float
    sample_rate: int
    voice_id: str
    filename: str


class VoiceProfile(BaseModel):
    id: str
    name: str
    gender: VoiceGender
    style: VoiceStyle
    language: Language
    sample_rate: int = 24000
    model_path: Optional[str] = None
    config_path: Optional[str] = None


class HealthResponse(BaseModel):
    status: str
    version: str
    voices_loaded: int
    models_loaded: int


BASE_DIR = Path(__file__).resolve().parent.parent
MODELS_DIR = BASE_DIR / "models"
VOICES_DIR = BASE_DIR / "voices"
AUDIO_DIR = BASE_DIR / "audio"
OUTPUT_DIR = BASE_DIR / "output"
CONFIG_DIR = BASE_DIR / "config"
DB_PATH = BASE_DIR / "ai_voice.db"

SAMPLE_RATE = 24000
CHUNK_SIZE = 1024
MAX_TEXT_LENGTH = 5000
