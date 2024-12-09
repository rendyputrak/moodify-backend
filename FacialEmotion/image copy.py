from fastapi import APIRouter, HTTPException, File, UploadFile, Depends, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from pathlib import Path
import shutil
from database import get_db
from models import Image

router = APIRouter()

# Folder untuk menyimpan gambar yang di-upload
UPLOAD_DIR = Path("./images")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

class ImageCreate(BaseModel):
    UserID: int
    ImagePath: str

# Fungsi untuk menyimpan file gambar ke direktori yang ditentukan
def save_uploaded_file(file: UploadFile) -> str:
    try:
        # Tentukan lokasi penyimpanan file
        file_location = UPLOAD_DIR / file.filename
        with open(file_location, "wb") as f:
            shutil.copyfileobj(file.file, f)  # Menyalin file ke lokasi penyimpanan
        return str(file_location)  # Kembalikan path file yang disimpan
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving file: {str(e)}")

# Endpoint untuk meng-upload gambar dan menyimpan path-nya ke database
@router.post("/images/", response_model=ImageCreate, status_code=status.HTTP_201_CREATED)
async def create_image(user_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    # Simpan file gambar dan dapatkan path-nya
    image_path = save_uploaded_file(file)
    
    # Buat URL untuk gambar
    image_url = f"http://localhost:8000/images/{file.filename}"  # Ganti dengan alamat server yang sesuai
    
    # Simpan informasi gambar ke dalam database
    db_image = Image(
        UserID=user_id,
        ImagePath=image_url  # Simpan URL gambar yang bisa diakses
    )
    db.add(db_image)
    db.commit()
    db.refresh(db_image)
    
    return db_image

# Endpoint untuk mendapatkan semua images
@router.get("/images/", status_code=status.HTTP_200_OK)
async def get_images(db: Session = Depends(get_db)):
    return db.query(Image).all()

# Endpoint untuk mendapatkan image berdasarkan user
@router.get("/images/{user_id}", status_code=status.HTTP_200_OK)
async def get_users(user_id: int, db: Session = Depends(get_db)):
    image = db.query(Image).filter(Image.UserID == user_id).all()
    if image is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Gambar tidak ditemukan!")
    return image

# Endpoint untuk mendapatkan image paling baru berdasarkan user_id
@router.get("/images/latest/{user_id}", status_code=status.HTTP_200_OK)
async def get_latest_image(user_id: int, db: Session = Depends(get_db)):
    latest_image = (
        db.query(Image)
        .filter(Image.UserID == user_id)
        .order_by(desc(Image.CreatedAt))  # Urutkan berdasarkan waktu terbaru
        .first()
    )
    if not latest_image:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Gambar terbaru tidak ditemukan!")
    return latest_image
