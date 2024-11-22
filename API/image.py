from fastapi import APIRouter, FastAPI, HTTPException, Depends, status
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
import models  
from database import engine, SessionLocal  
from pydantic import BaseModel, validator
from typing import List, Annotated
from database import get_db

router = APIRouter()

class ImageCreate(BaseModel):
    UserID: int
    ImagePath: str

# Endpoint untuk menambah image
@router.post("/images/", response_model=ImageCreate, status_code=status.HTTP_201_CREATED)
async def create_image(image: ImageCreate, db: Annotated[Session, Depends(get_db)]):
    db_image = models.Image(
        UserID=image.UserID,
        ImagePath=image.ImagePath
    )
    db.add(db_image)
    db.commit()
    db.refresh(db_image)
    return db_image

# Endpoint untuk mendapatkan semua images
@router.get("/images/", status_code=status.HTTP_200_OK)
async def get_images(db: Annotated[Session, Depends(get_db)]):
    return db.query(models.Image).all()

# Endpoint untuk mendapatkan image berdasarkan user
@router.get("/images/{user_id}", status_code=status.HTTP_200_OK)
async def get_users(user_id: int, db: Annotated[Session, Depends(get_db)]):
    user = db.query(models.Image).filter(models.Image.UserID == user_id).all()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Gambar tidak ditemukan!")
    return user
