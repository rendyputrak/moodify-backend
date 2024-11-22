from fastapi import APIRouter, FastAPI, HTTPException, Depends, status
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
import models  
from database import engine, SessionLocal  
from pydantic import BaseModel, validator
from typing import List, Annotated
from database import get_db

router = APIRouter()

class MoodRecapCreate(BaseModel):
    AnalysisID: int
    UserID: int
    MoodID: int

# Endpoint untuk menambah mood recap
@router.post("/mood_recap/", response_model=MoodRecapCreate, status_code=status.HTTP_201_CREATED)
async def create_mood_recap(mood_recap: MoodRecapCreate, db: Annotated[Session, Depends(get_db)]):
    db_mood_recap = models.MoodRecap(
        AnalysisID=mood_recap.AnalysisID,
        UserID=mood_recap.UserID,
        MoodID=mood_recap.MoodID
    )
    db.add(db_mood_recap)
    db.commit()
    db.refresh(db_mood_recap)
    return db_mood_recap

# Endpoint untuk mendapatkan semua mood recaps
@router.get("/mood_recap/", status_code=status.HTTP_200_OK)
async def get_mood_recap(db: Annotated[Session, Depends(get_db)]):
    return db.query(models.MoodRecap).all()