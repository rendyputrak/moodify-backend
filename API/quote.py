from fastapi import Depends, status, APIRouter, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, validator
from typing import List, Annotated
from database import get_db
from models import Quote

router = APIRouter()

class QuoteCreate(BaseModel):
    QuoteText: str
    QuoteAuthor: str
    MoodID: int
    RecapID: int

class QuoteResponse(BaseModel):
    QuoteText: str
    QuoteAuthor: str
    Mood: str

# Endpoint untuk menambah quote
@router.post("/quote/", response_model=QuoteCreate, status_code=status.HTTP_200_OK)
async def create_quote(quote: QuoteCreate, db: Annotated[Session, Depends(get_db)]):
    db_quote = Quote(
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
@router.get("/quote/", status_code=status.HTTP_200_OK)
async def get_quotes(db: Annotated[Session, Depends(get_db)]):
    return db.query(Quote).all()

@router.get("/quote/{mood}", response_model=List[QuoteResponse], status_code=status.HTTP_200_OK)
async def get_quotes_by_mood(mood: str, db: Annotated[Session, Depends(get_db)]):
    # Mencari quotes yang memiliki Mood yang sesuai dengan parameter mood
    quotes = db.query(Quote).filter(Quote.Mood == mood).all()
    
    if not quotes:
        raise HTTPException(status_code=404, detail=f"No quotes found for mood: {mood}")
    
    return quotes