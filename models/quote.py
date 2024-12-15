from sqlalchemy import Boolean, Column, Integer, String, Float, Date, Enum, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class Quote(Base):
    __tablename__ = "quotes"
    QuoteID = Column(Integer, primary_key=True, autoincrement=True)
    QuoteText = Column(String(255))
    QuoteAuthor = Column(String(100))
    Mood = Column(String(255))