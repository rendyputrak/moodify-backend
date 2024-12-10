from fastapi import APIRouter, FastAPI, HTTPException, Depends, status
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
import models  
from database import engine, SessionLocal  
from pydantic import BaseModel, validator
from typing import List, Annotated
from database import get_db

router = APIRouter()

class MusicDatasetCreate(BaseModel):
    MusicTitle: str
    MusicAlbum: str
    MusicArtist: str
    ReleaseDate: str
    SongUrl: str
    MoodClassification: str

class MusicDatasetResponse(BaseModel):
    MusicID: int
    MusicTitle: str
    MusicAlbum: str
    MusicArtist: str
    SpotifyID: str
    ReleaseDate: str
    SongUrl: str
    ImageUrl: str
    Duration: str
    MoodClassification: str

    class Config:
        orm_mode = True

mood_mapping = {
    "happy": ["Happy", "Calm"],
    "sad": ["Sad", "Calm"],
    "angry": ["Energetic", "Calm"],
    "disgust": ["Energetic", "Happy", "Calm"],
    "fear": ["Happy", "Calm"],
    "surprise": ["Energetic", "Happy", "Sad"],
    "neutral": ["Energetic", "Happy", "Calm", "Sad"]
}

# Endpoint untuk menambah music dataset
@router.post("/music_dataset/", response_model=MusicDatasetCreate, status_code=status.HTTP_201_CREATED)
async def create_music_dataset(dataset: MusicDatasetCreate, db: Annotated[Session, Depends(get_db)]):
    db_dataset = models.MusicDataset(
        MusicTitle=dataset.MusicTitle,
        MusicAlbum=dataset.MusicAlbum,
        MusicArtist=dataset.MusicArtist,
        ReleaseDate=dataset.ReleaseDate,
        SongUrl=dataset.SongUrl,
        MoodClassification=dataset.MoodClassification
    )
    db.add(db_dataset)
    db.commit()
    db.refresh(db_dataset)
    return db_dataset

# Endpoint untuk mendapatkan semua music datasets
@router.get("/music_dataset/", status_code=status.HTTP_200_OK)
async def get_music_dataset(db: Annotated[Session, Depends(get_db)]):
    return db.query(models.MusicDataset).all()

# Endpoint untuk mendapatkan lagu berdasarkan MoodClassification
@router.get("/music_dataset/mood/{mood}", response_model=List[MusicDatasetResponse], status_code=status.HTTP_200_OK)
async def get_music_by_mood(mood: str, db: Annotated[Session, Depends(get_db)]):
    # Validasi input mood
    if mood not in mood_mapping:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid mood. Valid options are: {', '.join(mood_mapping.keys())}"
        )

    # Ambil MoodClassification yang sesuai dengan mood
    mood_classifications = mood_mapping[mood]

    # Filter lagu berdasarkan MoodClassification yang sesuai
    songs = (
        db.query(models.MusicDataset)
        .filter(models.MusicDataset.MoodClassification.in_(mood_classifications))
        .all()
    )

    if not songs:
        raise HTTPException(status_code=404, detail=f"No songs found for mood: {mood}")

    return songs