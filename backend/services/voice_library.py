import json
import logging
from pathlib import Path
from typing import Dict, Optional, List
from ..core.config import VoiceProfile, VoiceGender, VoiceStyle, Language, VOICES_DIR

logger = logging.getLogger(__name__)


class VoiceLibrary:
    def __init__(self):
        self.voices: Dict[str, VoiceProfile] = {}
        self._initialize_default_voices()

    def _initialize_default_voices(self):
        default_voices = [
            VoiceProfile(
                id="female1", name="Female Soft",
                gender=VoiceGender.FEMALE, style=VoiceStyle.SOFT,
                language=Language.ENGLISH
            ),
            VoiceProfile(
                id="female2", name="Female Calm",
                gender=VoiceGender.FEMALE, style=VoiceStyle.CALM,
                language=Language.ENGLISH
            ),
            VoiceProfile(
                id="female3", name="Female Young",
                gender=VoiceGender.FEMALE, style=VoiceStyle.YOUNG,
                language=Language.ENGLISH
            ),
            VoiceProfile(
                id="female4", name="Female Professional",
                gender=VoiceGender.FEMALE, style=VoiceStyle.PROFESSIONAL,
                language=Language.ENGLISH
            ),
            VoiceProfile(
                id="female5", name="Female Emotional",
                gender=VoiceGender.FEMALE, style=VoiceStyle.EMOTIONAL,
                language=Language.ENGLISH
            ),
            VoiceProfile(
                id="male1", name="Male Deep",
                gender=VoiceGender.MALE, style=VoiceStyle.DEEP,
                language=Language.ENGLISH
            ),
            VoiceProfile(
                id="male2", name="Male Calm",
                gender=VoiceGender.MALE, style=VoiceStyle.CALM,
                language=Language.ENGLISH
            ),
            VoiceProfile(
                id="male3", name="Male Young",
                gender=VoiceGender.MALE, style=VoiceStyle.YOUNG,
                language=Language.ENGLISH
            ),
            VoiceProfile(
                id="male4", name="Male Professional",
                gender=VoiceGender.MALE, style=VoiceStyle.PROFESSIONAL,
                language=Language.ENGLISH
            ),
            VoiceProfile(
                id="male5", name="Male Friendly",
                gender=VoiceGender.MALE, style=VoiceStyle.FRIENDLY,
                language=Language.ENGLISH
            ),
        ]

        for voice in default_voices:
            self.voices[voice.id] = voice

        self._load_voice_configs()

    def _load_voice_configs(self):
        for voice_id, voice in self.voices.items():
            voice_dir = VOICES_DIR / voice_id
            config_file = voice_dir / "config.json"

            if config_file.exists():
                try:
                    with open(config_file, 'r') as f:
                        config = json.load(f)
                    voice.model_path = config.get('model_path')
                    voice.config_path = config.get('config_path')
                    if 'language' in config:
                        voice.language = Language(config['language'])
                    logger.info(f"Loaded config for voice: {voice_id}")
                except Exception as e:
                    logger.warning(f"Failed to load config for {voice_id}: {e}")

    def get_voice(self, voice_id: str) -> Optional[VoiceProfile]:
        return self.voices.get(voice_id)

    def list_voices(self) -> List[VoiceProfile]:
        return list(self.voices.values())

    def get_voices_by_gender(self, gender: VoiceGender) -> List[VoiceProfile]:
        return [v for v in self.voices.values() if v.gender == gender]

    def get_voices_by_language(self, language: Language) -> List[VoiceProfile]:
        return [v for v in self.voices.values() if v.language == language]

    def add_voice(self, profile: VoiceProfile) -> bool:
        if profile.id in self.voices:
            logger.warning(f"Voice {profile.id} already exists")
            return False

        self.voices[profile.id] = profile
        voice_dir = VOICES_DIR / profile.id
        voice_dir.mkdir(parents=True, exist_ok=True)

        config = {
            'id': profile.id,
            'name': profile.name,
            'gender': profile.gender.value,
            'style': profile.style.value,
            'language': profile.language.value,
            'model_path': profile.model_path,
            'config_path': profile.config_path,
        }

        config_file = voice_dir / "config.json"
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)

        logger.info(f"Added voice: {profile.id}")
        return True

    def remove_voice(self, voice_id: str) -> bool:
        if voice_id not in self.voices:
            return False

        del self.voices[voice_id]
        voice_dir = VOICES_DIR / voice_id
        if voice_dir.exists():
            import shutil
            shutil.rmtree(voice_dir)

        logger.info(f"Removed voice: {voice_id}")
        return True

    def get_voice_params(self, voice_id: str) -> Dict:
        voice = self.get_voice(voice_id)
        if not voice:
            return self._default_params()

        style_params = {
            VoiceStyle.SOFT: {"pitch_base": 1.1, "speed_base": 0.95, "volume_base": 0.85},
            VoiceStyle.CALM: {"pitch_base": 1.0, "speed_base": 0.9, "volume_base": 0.9},
            VoiceStyle.YOUNG: {"pitch_base": 1.15, "speed_base": 1.05, "volume_base": 1.0},
            VoiceStyle.PROFESSIONAL: {"pitch_base": 1.0, "speed_base": 1.0, "volume_base": 1.0},
            VoiceStyle.EMOTIONAL: {"pitch_base": 1.05, "speed_base": 1.0, "volume_base": 1.05},
            VoiceStyle.DEEP: {"pitch_base": 0.85, "speed_base": 0.95, "volume_base": 1.1},
            VoiceStyle.FRIENDLY: {"pitch_base": 1.05, "speed_base": 1.0, "volume_base": 1.0},
        }

        return style_params.get(voice.style, self._default_params())

    def _default_params(self) -> Dict:
        return {"pitch_base": 1.0, "speed_base": 1.0, "volume_base": 1.0}
