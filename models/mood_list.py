from sqlalchemy import Boolean, Column, Integer, String, Float, Date, Enum, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class MoodList(Base):
    __tablename__ = "mood_list"
    MoodID = Column(Integer, primary_key=True, autoincrement=True)
    ListMood = Column(Enum('Happy', 'Sad', 'Angry', 'Disgust', 'Fear', 'Surprise'))

    recaps = relationship("MoodRecap", back_populates="mood")
    quotes = relationship("Quote", back_populates="mood")