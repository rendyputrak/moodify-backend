from sqlalchemy import Boolean, Column, Integer, String, Float, Date, Enum, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class MusicDataset(Base):
    __tablename__ = "music_dataset"
    MusicID = Column(Integer, primary_key=True, autoincrement=True)
    MusicTitle = Column(String(255))
    MusicAlbum = Column(String(255))
    MusicArtist = Column(String(255))
    ReleaseDate = Column(Date)
    SongUrl = Column(String(255))
    MoodClassification = Column(Enum('Sad', 'Calm', 'Energetic', 'Happy'))
    CreatedAt = Column(TIMESTAMP, default=func.now(), nullable=False)
    UpdatedAt = Column(TIMESTAMP, default=func.now(), onupdate=func.now(), nullable=False)