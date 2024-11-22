from fastapi import APIRouter, FastAPI, HTTPException, Depends, status
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
import models  
from database import engine, SessionLocal  
from pydantic import BaseModel, validator
from typing import List, Annotated
from database import get_db

router = APIRouter()

class ExpressionAnalysisCreate(BaseModel):
    UserID: int
    ImageID: int
    MoodDetected: int
    SadScore: float
    AngryScore: float
    HappyScore: float
    DisgustScore: float
    FearScore: float
    SurpriseScore: float

# Endpoint untuk menambah expression analysis
@router.post("/expression_analysis/", response_model=ExpressionAnalysisCreate, status_code=status.HTTP_201_CREATED)
async def create_expression_analysis(analysis: ExpressionAnalysisCreate, db: Annotated[Session, Depends(get_db)]):
    db_analysis = models.ExpressionAnalysis(
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

# Endpoint untuk mendapatkan semua expression analyses
@router.get("/expression_analysis/", status_code=status.HTTP_200_OK)
async def get_expression_analysis(db: Annotated[Session, Depends(get_db)]):
    return db.query(models.ExpressionAnalysis).all()
