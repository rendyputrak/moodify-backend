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