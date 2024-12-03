from sqlalchemy import Boolean, Column, Integer, String, Float, Date, Enum, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class MoodRecap(Base):
    __tablename__ = "mood_recap"
    RecapID = Column(Integer, primary_key=True, autoincrement=True)
    AnalysisID = Column(Integer, ForeignKey("expression_analysis.AnalysisID"))
    UserID = Column(Integer, ForeignKey("users.UserID"))
    MoodID = Column(Integer, ForeignKey("mood_list.MoodID"))
    CreatedAt = Column(TIMESTAMP, default=func.now(), nullable=False)

    analysis = relationship("ExpressionAnalysis")
    user = relationship("User", back_populates="recaps")
    mood = relationship("MoodList", back_populates="recaps")