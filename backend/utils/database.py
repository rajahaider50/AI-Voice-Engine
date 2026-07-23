from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from ..core.config import DB_PATH

Base = declarative_base()


class AudioHistory(Base):
    __tablename__ = "audio_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    filename = Column(String, nullable=False)
    text = Column(String, nullable=False)
    voice_id = Column(String, nullable=False)
    language = Column(String, default="en")
    speed = Column(Float, default=1.0)
    pitch = Column(Float, default=1.0)
    volume = Column(Float, default=1.0)
    emotion = Column(String, default="neutral")
    duration = Column(Float, default=0.0)
    sample_rate = Column(Integer, default=24000)
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "filename": self.filename,
            "text": self.text,
            "voice_id": self.voice_id,
            "language": self.language,
            "speed": self.speed,
            "pitch": self.pitch,
            "volume": self.volume,
            "emotion": self.emotion,
            "duration": self.duration,
            "sample_rate": self.sample_rate,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class FavoriteAudio(Base):
    __tablename__ = "favorite_audio"

    id = Column(Integer, primary_key=True, autoincrement=True)
    audio_history_id = Column(Integer, nullable=False)
    label = Column(String, default="")
    created_at = Column(DateTime, default=datetime.utcnow)


engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)
SessionLocal = sessionmaker(bind=engine)


def init_db():
    Base.metadata.create_all(engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
