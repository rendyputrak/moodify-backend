from fastapi import APIRouter, FastAPI, HTTPException, Depends, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Annotated
from database import get_db
from models import ExpressionAnalysis

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

