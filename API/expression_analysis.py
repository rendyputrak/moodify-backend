from fastapi import APIRouter, FastAPI, HTTPException, Depends, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Annotated
from database import get_db
from models import ExpressionAnalysis
from sqlalchemy import func, desc
from API.user import get_current_user

router = APIRouter()

class ExpressionAnalysisCreate(BaseModel):
    UserID: int
    ImageID: int
    MoodDetected: str
    SadScore: float
    AngryScore: float
    HappyScore: float
    DisgustScore: float
    FearScore: float
    SurpriseScore: float
    NeutralScore: float

class ExpressionAnalysisResponse(BaseModel):
    UserID: int
    ImageID: int
    MoodDetected: str
    SadScore: str
    AngryScore: str
    HappyScore: str
    DisgustScore: str
    FearScore: str
    SurpriseScore: str
    NeutralScore: str
    CreatedAt: str
    
def convert_to_percentage(score: float) -> str:
    """Mengubah skor float menjadi persentase dengan format 'xx.xx%'."""
    return f"{score:.4f}%"  # Ambil 5 karakter saja

# Endpoint untuk mendapatkan expression analysis dari user
@router.get("/expression_analysis", response_model=List[ExpressionAnalysisResponse], status_code=status.HTTP_200_OK)
async def get_expression_analysis(
    db: Annotated[Session, Depends(get_db)],
    current_user: dict = Depends(get_current_user),  # Ambil user dari token
    skip: int = 0,  # Posisi mulai pagination
    limit: int = 10  # Jumlah data yang akan di-load per halaman
):
    user_id = current_user.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid user authentication")

    # Query dengan pengurutan berdasarkan CreatedAt descending, dan pagination dengan skip dan limit
    user_expression = (
        db.query(ExpressionAnalysis)
        .filter(ExpressionAnalysis.UserID == user_id)
        .order_by(desc(ExpressionAnalysis.CreatedAt))
        .offset(skip)  # Menentukan mulai dari record keberapa
        .limit(limit)  # Mengambil sejumlah limit data
        .all()
    )

    if not user_expression:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analisis ekspresi tidak ditemukan!")

    # Konversi skor menjadi persentase
    response = []
    for exp in user_expression:
        response.append({
            "UserID": exp.UserID,
            "ImageID": exp.ImageID,
            "MoodDetected": exp.MoodDetected,
            "SadScore": convert_to_percentage(exp.SadScore),
            "AngryScore": convert_to_percentage(exp.AngryScore),
            "HappyScore": convert_to_percentage(exp.HappyScore),
            "DisgustScore": convert_to_percentage(exp.DisgustScore),
            "FearScore": convert_to_percentage(exp.FearScore),
            "SurpriseScore": convert_to_percentage(exp.SurpriseScore),
            "NeutralScore": convert_to_percentage(exp.NeutralScore),
            "CreatedAt": exp.CreatedAt.strftime("%Y-%m-%d %H:%M:%S")
        })
    return response

# Endpoint untuk mendapatkan detail ekspresi terbaru dari user
@router.get("/expression_analysis/latest", status_code=status.HTTP_200_OK)
async def get_latest_expression_analysis(
    db: Annotated[Session, Depends(get_db)],
    current_user: dict = Depends(get_current_user)  # Ambil user dari token
):
    user_id = current_user.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid user authentication")

    # Mengambil ekspresi terbaru berdasarkan UserID dan diurutkan berdasarkan CreatedAt
    latest_expression = db.query(ExpressionAnalysis).filter(ExpressionAnalysis.UserID == user_id).order_by(ExpressionAnalysis.CreatedAt.desc()).first()
    
    if not latest_expression:
        # Jika tidak ada data ekspresi terbaru, set semua field menjadi None, kecuali MoodDetected
        return {
            "AnalysisID": None,
            "UserID": None,
            "ImageID": None,
            "MoodDetected": 'Neutral',
            "SadScore": None,
            "AngryScore": None,
            "HappyScore": None,
            "DisgustScore": None,
            "FearScore": None,
            "SurpriseScore": None,
            "NeutralScore": None,
            "CreatedAt": None
        }

    # Jika ada data ekspresi terbaru, kembalikan data tersebut
    return latest_expression

# Endpoint untuk mendapatkan jumlah mood yang terdeteksi per user berdasarkan MoodDetected
@router.get("/expression_analysis/mood_counts", status_code=status.HTTP_200_OK)
async def get_mood_counts_by_user(
    db: Annotated[Session, Depends(get_db)],
    current_user: dict = Depends(get_current_user)  # Ambil user dari token
):
    user_id = current_user.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid user authentication")

    # Menghitung jumlah mood yang terdeteksi berdasarkan MoodDetected dan UserID
    mood_counts = db.query(
        ExpressionAnalysis.MoodDetected,
        func.count().label('total')
    ).filter(ExpressionAnalysis.UserID == user_id) \
     .group_by(ExpressionAnalysis.MoodDetected).all()

    # Membuat dictionary untuk menyimpan jumlah mood per tipe
    mood_count_dict = {
        "Happy": 0,
        "Sad": 0,
        "Fear": 0,
        "Disgust": 0,
        "Angry": 0,
        "Surprise": 0,
        "Neutral": 0
    }

    # Menambahkan jumlah mood yang terdeteksi ke dalam dictionary
    for mood, count in mood_counts:
        if mood in mood_count_dict:
            mood_count_dict[mood] = count

    # Menambahkan total perhitungan semua mood
    total_moods = sum(mood_count_dict.values())

    # Menambahkan total ke dalam dictionary
    mood_count_dict["Total"] = total_moods

    return mood_count_dict
