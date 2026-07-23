# AI Voice Engine

## Quick Start

### 1. Install Python Dependencies

```bash
cd AI-Voice
pip install -r requirements.txt
```

### 2. Run Backend

```bash
python run.py
```

Backend will start at `http://localhost:8000`

API docs: `http://localhost:8000/docs`

### 3. Run Flutter App

```bash
cd AI-Voice/app
flutter pub get
flutter run
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/tts` | Generate speech from text |
| GET | `/api/v1/voices` | List all voices |
| GET | `/api/v1/voices/{gender}` | Filter voices by gender |
| GET | `/api/v1/audio/{filename}` | Download generated audio |
| GET | `/api/v1/history` | Get generation history |
| GET | `/api/v1/stats` | Get system stats |
| GET | `/api/v1/health` | Health check |

## Voice Profiles

### Female Voices
- **female1** - Female Soft
- **female2** - Female Calm
- **female3** - Female Young
- **female4** - Female Professional
- **female5** - Female Emotional

### Male Voices
- **male1** - Male Deep
- **male2** - Male Calm
- **male3** - Male Young
- **male4** - Male Professional
- **male5** - Male Friendly

## Controls

| Parameter | Range | Default |
|-----------|-------|---------|
| Speed | 0.5 - 2.0 | 1.0 |
| Pitch | 0.5 - 2.0 | 1.0 |
| Volume | 0.0 - 2.0 | 1.0 |
| Emotion | neutral/happy/sad/angry/surprised | neutral |
| Breath Effect | true/false | true |

## Supported Languages

- English (en)
- Urdu (ur)
- Hindi (hi)

## Example Request

```bash
curl -X POST http://localhost:8000/api/v1/tts \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello, this is a test of the AI Voice Engine.",
    "voice_id": "female1",
    "speed": 1.0,
    "pitch": 1.0,
    "emotion": "happy"
  }'
```

## Project Structure

```
AI-Voice/
├── models/              # ONNX/PyTorch models
├── voices/              # Voice profiles
│   ├── female1-5/
│   └── male1-5/
├── backend/
│   ├── api/             # FastAPI routes
│   ├── core/            # Config and models
│   ├── services/        # Business logic
│   └── utils/           # Database, helpers
├── app/                 # Flutter mobile app
├── audio/               # Temporary audio files
├── output/              # Generated audio
├── config/              # Configuration files
└── tests/               # Test files
```

## Roadmap

1. [x] Project structure
2. [x] FastAPI backend
3. [x] TTS pipeline
4. [x] Voice library (10 voices)
5. [x] Audio post-processing
6. [x] Flutter app
7. [ ] ONNX model integration
8. [ ] StyleTTS2 / XTTS v2
9. [ ] Multilingual TTS
10. [ ] Offline mode
