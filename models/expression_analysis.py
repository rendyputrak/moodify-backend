from sqlalchemy import Boolean, Column, Integer, String, Float, Date, Enum, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class ExpressionAnalysis(Base):
    __tablename__ = "expression_analysis"
    AnalysisID = Column(Integer, primary_key=True, autoincrement=True)
    UserID = Column(Integer, ForeignKey("users.UserID"))
    ImageID = Column(Integer, ForeignKey("images.ImageID"))
    MoodDetected = Column(Integer)
    SadScore = Column(Float)
    AngryScore = Column(Float)
    HappyScore = Column(Float)
    DisgustScore = Column(Float)
    FearScore = Column(Float)
    SurpriseScore = Column(Float)
    CreatedAt = Column(TIMESTAMP, default=func.now(), nullable=False)

    user = relationship("User", back_populates="analyses")
    image = relationship("Image", back_populates="analyses")