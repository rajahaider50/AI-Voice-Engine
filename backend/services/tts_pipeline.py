import logging
import uuid
import numpy as np
from pathlib import Path
from typing import Optional
from datetime import datetime

from ..core.config import TTSRequest, TTSResponse, OUTPUT_DIR, SAMPLE_RATE
from .text_processor import TextProcessor
from .tts_model import TTSModel
from .audio_processor import AudioProcessor
from .voice_library import VoiceLibrary

logger = logging.getLogger(__name__)


class TTSPipeline:
    def __init__(self):
        self.text_processor = TextProcessor()
        self.tts_model = TTSModel()
        self.audio_processor = AudioProcessor(sample_rate=SAMPLE_RATE)
        self.voice_library = VoiceLibrary()
        self._history = []

    def initialize(self):
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        logger.info("TTS Pipeline initialized")

    def process(self, request: TTSRequest) -> Optional[TTSResponse]:
        try:
            logger.info(f"Processing TTS request for voice: {request.voice_id}")

            cleaned_text = self.text_processor.clean_text(request.text)
            if not cleaned_text:
                logger.warning("Empty text after cleaning")
                return None

            voice_params = self.voice_library.get_voice_params(request.voice_id)

            sentences = self.text_processor.split_sentences(
                cleaned_text, request.language
            )

            audio_segments = []
            for sentence in sentences:
                segment = self._process_sentence(
                    sentence, request, voice_params
                )
                if segment is not None:
                    audio_segments.append(segment)

            if not audio_segments:
                logger.warning("No audio segments generated")
                return None

            final_audio = self.audio_processor.smooth_join(audio_segments)

            final_audio = self.audio_processor.adjust_speed(
                final_audio, request.speed
            )

            final_audio = self.audio_processor.adjust_volume(
                final_audio, request.volume
            )

            final_audio = self.audio_processor.normalize_loudness(final_audio)

            if request.breath_effect:
                final_audio = self.audio_processor.add_breathing(final_audio)

            filename = f"{request.voice_id}_{uuid.uuid4().hex[:8]}.wav"
            filepath = OUTPUT_DIR / filename

            success = self.audio_processor.save_audio(
                final_audio, str(filepath)
            )

            if not success:
                return None

            duration = self.audio_processor.get_duration(final_audio)

            response = TTSResponse(
                audio_url=f"/audio/{filename}",
                duration=round(duration, 2),
                sample_rate=SAMPLE_RATE,
                voice_id=request.voice_id,
                filename=filename,
            )

            self._add_to_history(request, response)

            logger.info(f"TTS completed: {filename} ({duration:.2f}s)")
            return response

        except Exception as e:
            logger.error(f"TTS processing failed: {e}")
            raise

    def _process_sentence(
        self, sentence: str, request: TTSRequest, voice_params: dict
    ) -> Optional[np.ndarray]:
        speed = request.speed * voice_params.get("speed_base", 1.0)
        pitch = request.pitch * voice_params.get("pitch_base", 1.0)
        volume = request.volume * voice_params.get("volume_base", 1.0)

        raw_audio = self.tts_model.synthesize(
            sentence,
            voice_id=request.voice_id,
            speed=speed,
            pitch=pitch,
            sample_rate=SAMPLE_RATE,
        )

        if raw_audio is None:
            return None

        if request.emotion.value != "neutral":
            raw_audio = self.audio_processor.apply_emotion(
                raw_audio, request.emotion.value
            )

        raw_audio = self.audio_processor.adjust_pitch(raw_audio, pitch)

        return raw_audio

    def _add_to_history(self, request: TTSRequest, response: TTSResponse):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "text": request.text[:100],
            "voice_id": request.voice_id,
            "language": request.language.value,
            "duration": response.duration,
            "filename": response.filename,
        }
        self._history.append(entry)

        if len(self._history) > 100:
            self._history = self._history[-100:]

    def get_history(self) -> list:
        return list(reversed(self._history))

    def get_stats(self) -> dict:
        return {
            "total_generated": len(self._history),
            "voices_available": len(self.voice_library.list_voices()),
            "model_loaded": self.tts_model.is_loaded,
            "sample_rate": SAMPLE_RATE,
        }
