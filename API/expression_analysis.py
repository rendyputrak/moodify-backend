from fastapi import APIRouter, FastAPI, HTTPException, Depends, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Annotated
from database import get_db
from models import ExpressionAnalysis
from sqlalchemy import func

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

# Endpoint untuk menambah expression analysis
@router.post("/expression_analysis/", response_model=ExpressionAnalysisCreate, status_code=status.HTTP_201_CREATED)
async def create_expression_analysis(analysis: ExpressionAnalysisCreate, db: Annotated[Session, Depends(get_db)]):
    db_analysis = ExpressionAnalysis(
        UserID=analysis.UserID,
        ImageID=analysis.ImageID,
        MoodDetected=analysis.MoodDetected,
        SadScore=analysis.SadScore,
        AngryScore=analysis.AngryScore,
        HappyScore=analysis.HappyScore,
        DisgustScore=analysis.DisgustScore,
        FearScore=analysis.FearScore,
        SurpriseScore=analysis.SurpriseScore
    )
    db.add(db_analysis)
    db.commit()
    db.refresh(db_analysis)
    return db_analysis

# Endpoint untuk mendapatkan semua expression analysis
@router.get("/expression_analysis/", status_code=status.HTTP_200_OK)
async def get_expression_analysis(db: Annotated[Session, Depends(get_db)]):
    return db.query(ExpressionAnalysis).all()

# Endpoint untuk mendapatkan expression analysis dari user
@router.get("/expression_analysis/{user_id}", status_code=status.HTTP_200_OK)
async def get_expression_analysis(user_id: int, db: Annotated[Session, Depends(get_db)]):
    user_expression = db.query(ExpressionAnalysis).filter(ExpressionAnalysis.UserID == user_id).all()
    if not user_expression:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analisis ekspresi tidak ditemukan!")
    return user_expression

# Endpoint untuk mendapatkan detail ekspresi terbaru dari user
@router.get("/expression_analysis/latest/{user_id}", status_code=status.HTTP_200_OK)
async def get_latest_expression_analysis(user_id: int, db: Annotated[Session, Depends(get_db)]):
    # Mengambil ekspresi terbaru berdasarkan UserID dan diurutkan berdasarkan CreatedAt
    latest_expression = db.query(ExpressionAnalysis).filter(ExpressionAnalysis.UserID == user_id).order_by(ExpressionAnalysis.CreatedAt.desc()).first()
    if not latest_expression:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analisis ekspresi terbaru tidak ditemukan!")
    return latest_expression

# Endpoint untuk mendapatkan jumlah mood yang terdeteksi per user berdasarkan MoodDetected
@router.get("/expression_analysis/mood_counts/{user_id}", status_code=status.HTTP_200_OK)
async def get_mood_counts_by_user(user_id: int, db: Annotated[Session, Depends(get_db)]):
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
        "Surprised": 0
    }

    # Menambahkan jumlah mood yang terdeteksi ke dalam dictionary
    for mood, count in mood_counts:
        if mood in mood_count_dict:
            mood_count_dict[mood] = count

    return mood_count_dict

