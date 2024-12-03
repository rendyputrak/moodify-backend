from fastapi import APIRouter, FastAPI, HTTPException, Depends, status
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
import models  
from database import engine, SessionLocal  
from pydantic import BaseModel, validator
from typing import List, Annotated
from database import get_db
from models import MoodList

router = APIRouter()

class MoodListCreate(BaseModel):
    ListMood: str

# Endpoint untuk menambah mood list
@router.post("/mood_list/", response_model=MoodListCreate, status_code=status.HTTP_201_CREATED)
async def create_mood_list(mood_list: MoodListCreate, db: Annotated[Session, Depends(get_db)]):
    db_mood = MoodList(
        ListMood=mood_list.ListMood
    )
    db.add(db_mood)
    db.commit()
    db.refresh(db_mood)
    return db_mood

# Endpoint untuk mendapatkan semua mood lists
@router.get("/mood_list/", status_code=status.HTTP_200_OK)
async def get_mood_list(db: Annotated[Session, Depends(get_db)]):
    return db.query(MoodList).all()

# Endpoint untuk mendapatkan semua mood lists
@router.get("/mood_list/{mood_id}", status_code=status.HTTP_200_OK)
async def get_mood_list(mood_id: int, db: Annotated[Session, Depends(get_db)]):
    mood_list = db.query(MoodList).filter(MoodList.MoodID == mood_id).all()