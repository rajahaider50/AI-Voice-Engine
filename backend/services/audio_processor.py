import numpy as np
import soundfile as sf
from typing import Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class AudioProcessor:
    def __init__(self, sample_rate: int = 24000):
        self.sample_rate = sample_rate

    def adjust_speed(self, audio: np.ndarray, speed: float) -> np.ndarray:
        if speed == 1.0:
            return audio

        indices = np.round(np.arange(0, len(audio), speed)).astype(int)
        indices = indices[indices < len(audio)]
        return audio[indices]

    def adjust_pitch(self, audio: np.ndarray, pitch: float) -> np.ndarray:
        if pitch == 1.0:
            return audio

        try:
            import librosa
            shifted = librosa.effects.pitch_shift(
                audio.astype(np.float32),
                sr=self.sample_rate,
                n_steps=np.log2(pitch) * 12
            )
            return shifted
        except Exception as e:
            logger.warning(f"Pitch shift failed, using simple resampling: {e}")
            return self._simple_pitch_shift(audio, pitch)

    def _simple_pitch_shift(self, audio: np.ndarray, pitch: float) -> np.ndarray:
        indices = np.arange(0, len(audio), pitch)
        indices = indices[indices < len(audio)].astype(int)
        return audio[indices]

    def adjust_volume(self, audio: np.ndarray, volume: float) -> np.ndarray:
        adjusted = audio * volume
        max_val = np.max(np.abs(adjusted))
        if max_val > 1.0:
            adjusted = adjusted / max_val
        return adjusted

    def normalize_loudness(self, audio: np.ndarray, target_db: float = -20.0) -> np.ndarray:
        rms = np.sqrt(np.mean(audio ** 2))
        if rms == 0:
            return audio

        current_db = 20 * np.log10(rms)
        gain_db = target_db - current_db
        gain = 10 ** (gain_db / 20)
        normalized = audio * gain

        max_val = np.max(np.abs(normalized))
        if max_val > 0.99:
            normalized = normalized * (0.99 / max_val)

        return normalized

    def reduce_noise(self, audio: np.ndarray) -> np.ndarray:
        try:
            import noisereduce as nr
            reduced = nr.reduce_noise(
                y=audio.astype(np.float32),
                sr=self.sample_rate,
                prop_decrease=0.8
            )
            return reduced
        except Exception as e:
            logger.warning(f"Noise reduction failed: {e}")
            return self._simple_noise_reduction(audio)

    def _simple_noise_reduction(self, audio: np.ndarray) -> np.ndarray:
        threshold = np.mean(np.abs(audio)) * 0.1
        mask = np.abs(audio) > threshold
        return audio * mask

    def add_breathing(self, audio: np.ndarray, breath_duration: float = 0.15) -> np.ndarray:
        breath_samples = int(breath_duration * self.sample_rate)
        breath = np.random.randn(breath_samples) * 0.02

        t = np.linspace(0, np.pi, breath_samples)
        breath *= np.sin(t)

        word_boundaries = self._find_word_boundaries(audio)
        if not word_boundaries:
            return audio

        result = audio.copy()
        offset = 0
        for boundary in word_boundaries[:5]:
            insert_pos = boundary + offset
            if insert_pos < len(result):
                result = np.concatenate([
                    result[:insert_pos],
                    breath,
                    result[insert_pos:]
                ])
                offset += breath_samples

        return result

    def _find_word_boundaries(self, audio: np.ndarray, threshold: float = 0.01) -> list:
        frame_length = int(0.02 * self.sample_rate)
        hop_length = int(0.01 * self.sample_rate)

        boundaries = []
        for i in range(0, len(audio) - frame_length, hop_length):
            frame = audio[i:i + frame_length]
            energy = np.sqrt(np.mean(frame ** 2))
            if energy < threshold:
                boundaries.append(i)

        return boundaries

    def smooth_join(self, audio_segments: list) -> np.ndarray:
        if not audio_segments:
            return np.array([], dtype=np.float32)

        if len(audio_segments) == 1:
            return audio_segments[0]

        fade_length = int(0.02 * self.sample_rate)
        result = audio_segments[0]

        for segment in audio_segments[1:]:
            if len(result) < fade_length or len(segment) < fade_length:
                result = np.concatenate([result, segment])
                continue

            fade_out = np.linspace(1, 0, fade_length)
            fade_in = np.linspace(0, 1, fade_length)

            result[-fade_length:] *= fade_out
            segment[:fade_length] *= fade_in

            overlap = int(0.01 * self.sample_rate)
            result[-overlap:] += segment[:overlap]
            result = np.concatenate([result, segment[overlap:]])

        return result

    def apply_emotion(self, audio: np.ndarray, emotion: str) -> np.ndarray:
        emotion_params = {
            "happy": {"speed_mod": 1.1, "pitch_mod": 1.05, "volume_mod": 1.1},
            "sad": {"speed_mod": 0.9, "pitch_mod": 0.95, "volume_mod": 0.85},
            "angry": {"speed_mod": 1.15, "pitch_mod": 1.1, "volume_mod": 1.2},
            "surprised": {"speed_mod": 1.2, "pitch_mod": 1.15, "volume_mod": 1.1},
            "fearful": {"speed_mod": 1.05, "pitch_mod": 1.1, "volume_mod": 0.9},
            "neutral": {"speed_mod": 1.0, "pitch_mod": 1.0, "volume_mod": 1.0},
        }

        params = emotion_params.get(emotion, emotion_params["neutral"])

        result = self.adjust_speed(audio, params["speed_mod"])
        result = self.adjust_pitch(result, params["pitch_mod"])
        result = self.adjust_volume(result, params["volume_mod"])

        return result

    def save_audio(self, audio: np.ndarray, filepath: str, format: str = "wav") -> bool:
        try:
            filepath = Path(filepath)
            filepath.parent.mkdir(parents=True, exist_ok=True)

            audio_int16 = (audio * 32767).astype(np.int16)
            sf.write(str(filepath), audio_int16, self.sample_rate, subtype='PCM_16')
            logger.info(f"Audio saved: {filepath}")
            return True
        except Exception as e:
            logger.error(f"Failed to save audio: {e}")
            return False

    def load_audio(self, filepath: str) -> Optional[np.ndarray]:
        try:
            audio, sr = sf.read(filepath)
            if sr != self.sample_rate:
                import librosa
                audio = librosa.resample(audio, orig_sr=sr, target_sr=self.sample_rate)
            return audio.astype(np.float32)
        except Exception as e:
            logger.error(f"Failed to load audio: {e}")
            return None

    def get_duration(self, audio: np.ndarray) -> float:
        return len(audio) / self.sample_rate
