from sqlalchemy import Boolean, Column, Integer, String, Float, Date, Enum, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class Image(Base):
    __tablename__ = "images"
    ImageID = Column(Integer, primary_key=True, autoincrement=True)
    UserID = Column(Integer, ForeignKey("users.UserID"))
    ImagePath = Column(String(255))
    CreatedAt = Column(TIMESTAMP, default=func.now())

    user = relationship("User", back_populates="images")
    analyses = relationship("ExpressionAnalysis", back_populates="image")