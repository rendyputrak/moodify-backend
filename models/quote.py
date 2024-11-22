from sqlalchemy import Boolean, Column, Integer, String, Float, Date, Enum, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class Quote(Base):
    __tablename__ = "quotes"
    QuoteID = Column(Integer, primary_key=True, autoincrement=True)
    QuoteText = Column(String(255))
    QuoteAuthor = Column(String(100))
    MoodID = Column(Integer, ForeignKey("mood_list.MoodID"))
    RecapID = Column(Integer, ForeignKey("mood_recap.RecapID"))
    CreatedAt = Column(TIMESTAMP, default=func.now())

    mood = relationship("MoodList", back_populates="quotes")
    recap = relationship("MoodRecap")
    