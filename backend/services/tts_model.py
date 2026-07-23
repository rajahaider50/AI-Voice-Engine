import os
import numpy as np
from pathlib import Path
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class TTSModel:
    def __init__(self):
        self.model = None
        self.session = None
        self.is_loaded = False
        self.model_type = None

    def load_onnx_model(self, model_path: str) -> bool:
        try:
            import onnxruntime as ort
            self.session = ort.InferenceSession(model_path)
            self.is_loaded = True
            self.model_type = "onnx"
            logger.info(f"Loaded ONNX model: {model_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to load ONNX model: {e}")
            return False

    def load_pytorch_model(self, model_path: str) -> bool:
        try:
            import torch
            self.model = torch.load(model_path, map_location='cpu')
            self.model.eval()
            self.is_loaded = True
            self.model_type = "pytorch"
            logger.info(f"Loaded PyTorch model: {model_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to load PyTorch model: {e}")
            return False

    def synthesize(self, text: str, voice_id: str, **kwargs) -> Optional[np.ndarray]:
        if not self.is_loaded:
            logger.warning("Model not loaded, using fallback synthesis")
            return self._fallback_synthesis(text, **kwargs)

        if self.model_type == "onnx":
            return self._onnx_inference(text, voice_id, **kwargs)
        elif self.model_type == "pytorch":
            return self._pytorch_inference(text, voice_id, **kwargs)

        return self._fallback_synthesis(text, **kwargs)

    def _onnx_inference(self, text: str, voice_id: str, **kwargs) -> np.ndarray:
        try:
            input_text = self._tokenize(text)
            inputs = {
                'input_ids': input_text,
                'voice_id': np.array([hash(voice_id) % 100], dtype=np.int64)
            }
            if 'speed' in kwargs:
                inputs['speed'] = np.array([kwargs['speed']], dtype=np.float32)
            if 'pitch' in kwargs:
                inputs['pitch'] = np.array([kwargs['pitch']], dtype=np.float32)

            outputs = self.session.run(None, inputs)
            audio = outputs[0].squeeze()
            return audio
        except Exception as e:
            logger.error(f"ONNX inference failed: {e}")
            return self._fallback_synthesis(text, **kwargs)

    def _pytorch_inference(self, text: str, voice_id: str, **kwargs) -> np.ndarray:
        try:
            import torch
            with torch.no_grad():
                input_text = self._tokenize(text)
                output = self.model(input_text)
                audio = output.cpu().numpy().squeeze()
                return audio
        except Exception as e:
            logger.error(f"PyTorch inference failed: {e}")
            return self._fallback_synthesis(text, **kwargs)

    def _fallback_synthesis(self, text: str, **kwargs) -> np.ndarray:
        speed = kwargs.get('speed', 1.0)
        pitch = kwargs.get('pitch', 1.0)
        sample_rate = kwargs.get('sample_rate', 24000)

        duration = len(text.split()) / (2.5 * speed)
        t = np.linspace(0, duration, int(sample_rate * duration))

        base_freq = 200 * pitch
        audio = np.sin(2 * np.pi * base_freq * t) * 0.3

        envelope = np.ones_like(audio)
        fade_samples = int(0.05 * sample_rate)
        envelope[:fade_samples] = np.linspace(0, 1, fade_samples)
        envelope[-fade_samples:] = np.linspace(1, 0, fade_samples)
        audio *= envelope

        words = text.split()
        word_duration = duration / max(len(words), 1)
        for i, word in enumerate(words):
            start = int(i * word_duration * sample_rate)
            end = int((i + 0.8) * word_duration * sample_rate)
            if end > len(audio):
                end = len(audio)
            word_audio = audio[start:end]
            amplitude = 0.2 + 0.3 * np.random.random()
            audio[start:end] = word_audio * (amplitude / max(np.max(np.abs(word_audio)), 0.01))

        return audio.astype(np.float32)

    def _tokenize(self, text: str) -> np.ndarray:
        tokens = [ord(c) % 1000 for c in text[:512]]
        tokens = tokens + [0] * (512 - len(tokens))
        return np.array([tokens], dtype=np.int64)

    def unload(self):
        self.model = None
        self.session = None
        self.is_loaded = False
        self.model_type = None
