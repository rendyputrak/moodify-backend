from fastapi import APIRouter, HTTPException, Depends, status, UploadFile, File, Form, Query
from sqlalchemy import desc
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Annotated
from API.user import get_current_user
from database import get_db
from models import Image
import os
from uuid import uuid4
import shutil
from fastapi.responses import FileResponse##, StreamingResponse
# from PIL import Image as PILImage
# from PIL import ImageOps
# from io import BytesIO

router = APIRouter()

# Ensure the directory for saving images exists
UPLOAD_DIR = "images/user-faces"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# Endpoint untuk menambah image (dengan upload gambar)
@router.post("/images/", status_code=status.HTTP_201_CREATED)
async def create_image(
    user_id: int = Form(...),  # Receive UserID from form data
    image: UploadFile = File(...),  # Receive file from the request
    db: Session = Depends(get_db)
):
    try:
        # Generate a unique filename using UUID
        file_extension = os.path.splitext(image.filename)[1]
        unique_filename = f"{uuid4().hex}{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)

        # Save the uploaded file to the server's disk
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

        # Save the image information in the database
        db_image = Image(
            UserID=user_id,
            ImagePath=f"images/{unique_filename}"  # Store relative path to the images folder
        )
        db.add(db_image)
        db.commit()
        db.refresh(db_image)

        return {"UserID": user_id, "ImagePath": db_image.ImagePath}

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    
# Endpoint untuk mendapatkan semua images
@router.get("/images", status_code=status.HTTP_200_OK)
async def get_images(db: Annotated[Session, Depends(get_db)]):
    return db.query(Image).all()

# Endpoint untuk mendapatkan image berdasarkan user
@router.get("/images/user/{user_id}", status_code=status.HTTP_200_OK)
async def get_images_by_user(user_id: int, db: Annotated[Session, Depends(get_db)]):
    images = db.query(Image).filter(Image.UserID == user_id).all()
    if not images:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Gambar tidak ditemukan untuk user ini!")
    return images

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
    
# Endpoint untuk mendapatkan gambar berdasarkan ImageID
@router.get("/images/{image_id}", status_code=status.HTTP_200_OK)
async def get_image_by_id(image_id: int, db: Annotated[Session, Depends(get_db)]):
    # Cari gambar berdasarkan ImageID
    db_image = db.query(Image).filter(Image.ImageID == image_id).first()
    
    if not db_image:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Gambar tidak ditemukan!")
    
    # Ambil path gambar dari database
    file_path = db_image.ImagePath
    
    # Validasi apakah file benar-benar ada di sistem
    if not os.path.exists(file_path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File gambar tidak ditemukan di server!")
    
    # Tentukan media_type berdasarkan ekstensi file
    file_extension = os.path.splitext(file_path)[1].lower()
    media_types = {
        ".jpeg": "image/jpeg",
        ".jpg": "image/jpg",
        ".png": "image/png",
    }
    media_type = media_types.get(file_extension, "application/octet-stream")  # Default jika tidak cocok

    # Return file sebagai FileResponse
    return FileResponse(file_path, media_type=media_type)
