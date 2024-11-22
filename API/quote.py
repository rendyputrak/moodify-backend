from fastapi import Depends, status, APIRouter
from sqlalchemy.orm import Session
import models   
from pydantic import BaseModel, validator
from typing import List, Annotated
from database import get_db

router = APIRouter()

class QuoteCreate(BaseModel):
    QuoteText: str
    QuoteAuthor: str
    MoodID: int
    RecapID: int

# Endpoint untuk menambah quote
@router.post("/quotes/", response_model=QuoteCreate, status_code=status.HTTP_201_CREATED)
async def create_quote(quote: QuoteCreate, db: Annotated[Session, Depends(get_db)]):
    db_quote = models.Quote(
        QuoteText=quote.QuoteText,
        QuoteAuthor=quote.QuoteAuthor,
        MoodID=quote.MoodID,
        RecapID=quote.RecapID
    )
    db.add(db_quote)
    db.commit()
    db.refresh(db_quote)
    return db_quote

# Endpoint untuk mendapatkan semua quotes
@router.get("/quotes/", status_code=status.HTTP_200_OK)
async def get_quotes(db: Annotated[Session, Depends(get_db)]):
    return db.query(models.Quote).all()