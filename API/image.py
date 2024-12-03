from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy import desc
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Annotated
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

# Endpoint untuk mendapatkan image paling baru berdasarkan user_id
@router.get("/images/latest/{user_id}", status_code=status.HTTP_200_OK)
async def get_latest_image(user_id: int, db: Annotated[Session, Depends(get_db)]):
    latest_image = (
        db.query(Image)
        .filter(Image.UserID == user_id)
        .order_by(desc(Image.CreatedAt))  # Urutkan berdasarkan waktu terbaru
        .first()
    )
    if not latest_image:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Gambar terbaru tidak ditemukan!")
    return latest_image
