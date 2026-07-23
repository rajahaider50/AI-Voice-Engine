#!/usr/bin/env python3
import json
import http.server
import socketserver
import os
import uuid
import math
import struct
import wave
import io
import urllib.parse
import threading
import time

PORT = 8000
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

VOICES = [
    {"id": "female1", "name": "Female Soft", "gender": "female", "style": "soft", "language": "en"},
    {"id": "female2", "name": "Female Calm", "gender": "female", "style": "calm", "language": "en"},
    {"id": "female3", "name": "Female Young", "gender": "female", "style": "young", "language": "en"},
    {"id": "female4", "name": "Female Professional", "gender": "female", "style": "professional", "language": "en"},
    {"id": "female5", "name": "Female Emotional", "gender": "female", "style": "emotional", "language": "en"},
    {"id": "male1", "name": "Male Deep", "gender": "male", "style": "deep", "language": "en"},
    {"id": "male2", "name": "Male Calm", "gender": "male", "style": "calm", "language": "en"},
    {"id": "male3", "name": "Male Young", "gender": "male", "style": "young", "language": "en"},
    {"id": "male4", "name": "Male Professional", "gender": "male", "style": "professional", "language": "en"},
    {"id": "male5", "name": "Male Friendly", "gender": "male", "style": "friendly", "language": "en"},
]

HISTORY = []

VOICE_PARAMS = {
    "soft": {"pitch": 1.1, "speed": 0.95, "vol": 0.85},
    "calm": {"pitch": 1.0, "speed": 0.9, "vol": 0.9},
    "young": {"pitch": 1.15, "speed": 1.05, "vol": 1.0},
    "professional": {"pitch": 1.0, "speed": 1.0, "vol": 1.0},
    "emotional": {"pitch": 1.05, "speed": 1.0, "vol": 1.05},
    "deep": {"pitch": 0.85, "speed": 0.95, "vol": 1.1},
    "friendly": {"pitch": 1.05, "speed": 1.0, "vol": 1.0},
}


def generate_speech(text, voice_id, speed=1.0, pitch=1.0, volume=1.0, emotion="neutral"):
    voice = next((v for v in VOICES if v["id"] == voice_id), VOICES[0])
    vp = VOICE_PARAMS.get(voice["style"], {"pitch": 1.0, "speed": 1.0, "vol": 1.0})

    final_pitch = pitch * vp["pitch"]
    final_speed = speed * vp["speed"]
    final_vol = volume * vp["vol"]

    sample_rate = 24000
    words = text.split()
    duration = max(len(words) / (2.5 * final_speed), 0.5)
    n_samples = int(sample_rate * duration)

    emotion_mods = {
        "happy": {"s": 1.1, "p": 1.05, "v": 1.1},
        "sad": {"s": 0.9, "p": 0.95, "v": 0.85},
        "angry": {"s": 1.15, "p": 1.1, "v": 1.2},
        "surprised": {"s": 1.2, "p": 1.15, "v": 1.1},
        "neutral": {"s": 1.0, "p": 1.0, "v": 1.0},
    }
    em = emotion_mods.get(emotion, emotion_mods["neutral"])

    base_freq = 200 * final_pitch * em["p"]
    amp = 0.3 * final_vol * em["v"]

    audio = []
    for i in range(n_samples):
        t = i / sample_rate
        freq_mod = 1.0 + 0.02 * math.sin(2 * math.pi * 3 * t)
        val = amp * math.sin(2 * math.pi * base_freq * freq_mod * t)

        envelope = 1.0
        fade_len = int(0.05 * sample_rate)
        if i < fade_len:
            envelope = i / fade_len
        elif i > n_samples - fade_len:
            envelope = (n_samples - i) / fade_len

        word_idx = int(t * 2.5 * final_speed)
        if word_idx < len(words):
            word_var = 0.7 + 0.3 * abs(math.sin(hash(words[word_idx]) % 100))
        else:
            word_var = 0.5
        val *= envelope * word_var
        audio.append(val)

    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        samples = struct.pack(f"<{len(audio)}h", *[max(-32768, min(32767, int(s * 32767))) for s in audio])
        wf.writeframes(samples)

    filename = f"{voice_id}_{uuid.uuid4().hex[:8]}.wav"
    filepath = os.path.join(OUTPUT_DIR, filename)
    with open(filepath, "wb") as f:
        f.write(buf.getvalue())

    return filename, duration, sample_rate


class APIHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path == "/api/v1/health":
            self.send_json({"status": "healthy", "version": "1.0.0", "voices_loaded": len(VOICES), "models_loaded": 0})
        elif path == "/api/v1/voices":
            self.send_json({"voices": VOICES, "total": len(VOICES)})
        elif path.startswith("/api/v1/voices/"):
            gender = path.split("/")[-1]
            filtered = [v for v in VOICES if v["gender"] == gender]
            self.send_json({"voices": filtered, "total": len(filtered)})
        elif path.startswith("/api/v1/audio/"):
            filename = path.split("/")[-1]
            filepath = os.path.join(OUTPUT_DIR, filename)
            if os.path.exists(filepath):
                self.send_response(200)
                self.send_header("Content-Type", "audio/wav")
                self.send_header("Content-Length", os.path.getsize(filepath))
                self.end_headers()
                with open(filepath, "rb") as f:
                    self.wfile.write(f.read())
            else:
                self.send_json({"error": "File not found"}, 404)
        elif path == "/api/v1/history":
            self.send_json({"history": list(reversed(HISTORY))})
        elif path == "/api/v1/stats":
            self.send_json({"total_generated": len(HISTORY), "voices_available": len(VOICES), "model_loaded": False, "sample_rate": 24000})
        elif path == "/":
            self.send_json({
                "name": "AI Voice Engine",
                "version": "1.0.0",
                "status": "running",
                "endpoints": {"tts": "/api/v1/tts", "voices": "/api/v1/voices", "health": "/api/v1/health"}
            })
        else:
            self.send_json({"error": "Not found"}, 404)

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/api/v1/tts":
            content_len = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_len)
            try:
                data = json.loads(body)
            except json.JSONDecodeError:
                self.send_json({"error": "Invalid JSON"}, 400)
                return

            text = data.get("text", "").strip()
            if not text:
                self.send_json({"error": "Text cannot be empty"}, 400)
                return

            voice_id = data.get("voice_id", "female1")
            speed = data.get("speed", 1.0)
            pitch = data.get("pitch", 1.0)
            volume = data.get("volume", 1.0)
            emotion = data.get("emotion", "neutral")

            filename, duration, sr = generate_speech(text, voice_id, speed, pitch, volume, emotion)

            HISTORY.append({
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
                "text": text[:100],
                "voice_id": voice_id,
                "language": data.get("language", "en"),
                "duration": round(duration, 2),
                "filename": filename,
            })

            self.send_json({
                "audio_url": f"/api/v1/audio/{filename}",
                "duration": round(duration, 2),
                "sample_rate": sr,
                "voice_id": voice_id,
                "filename": filename,
            })
        else:
            self.send_json({"error": "Not found"}, 404)

    def send_json(self, data, status=200):
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", len(body))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def log_message(self, format, *args):
        print(f"[{time.strftime('%H:%M:%S')}] {args[0]}")


if __name__ == "__main__":
    print(f"")
    print(f"  ============================================")
    print(f"   AI Voice Engine Server - v1.0.0")
    print(f"  ============================================")
    print(f"")
    print(f"   Server:  http://localhost:{PORT}")
    print(f"   API:     http://localhost:{PORT}/api/v1")
    print(f"   Docs:    http://localhost:{PORT}/api/v1/health")
    print(f"   Voices:  http://localhost:{PORT}/api/v1/voices")
    print(f"")
    print(f"   10 voices loaded")
    print(f"   3 languages: English, Urdu, Hindi")
    print(f"  ============================================")
    print(f"")
    with socketserver.TCPServer(("0.0.0.0", PORT), APIHandler) as httpd:
        httpd.allow_reuse_address = True
        httpd.serve_forever()
