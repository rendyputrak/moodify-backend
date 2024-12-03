from fastapi import APIRouter, FastAPI, HTTPException, Depends, status
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
import models  
from database import engine, SessionLocal  
from pydantic import BaseModel, validator
from typing import List, Annotated
from database import get_db
from models import Image

router = APIRouter()

class ImageCreate(BaseModel):
    UserID: int
    ImagePath: str

# Endpoint untuk menambah image
@router.post("/images/", response_model=ImageCreate, status_code=status.HTTP_201_CREATED)
async def create_image(image: ImageCreate, db: Annotated[Session, Depends(get_db)]):
    db_image = Image(
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
    return db.query(Image).all()

# Endpoint untuk mendapatkan image berdasarkan user
@router.get("/images/{user_id}", status_code=status.HTTP_200_OK)
async def get_users(user_id: int, db: Annotated[Session, Depends(get_db)]):
    image = db.query(Image).filter(Image.UserID == user_id).all()
    if image is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Gambar tidak ditemukan!")
    return image
