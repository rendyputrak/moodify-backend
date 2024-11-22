from sqlalchemy import Boolean, Column, Integer, String, Float, Date, Enum, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class User(Base):
    __tablename__ = "users"
    UserID = Column(Integer, primary_key=True, autoincrement=True)
    Email = Column(String(255), nullable=False)
    Password = Column(String(255), nullable=False)
    Firstname = Column(String(100))
    Lastname = Column(String(100))
    Gender = Column(Enum('Laki-laki', 'Perempuan'))
    BirthDate = Column(Date)
    Avatar = Column(String(255), nullable=True)
    createdAt = Column(TIMESTAMP, default=func.now())
    updatedAt = Column(TIMESTAMP, default=func.now(), onupdate=func.now())

    images = relationship("Image", back_populates="user")
    analyses = relationship("ExpressionAnalysis", back_populates="user")
    recaps = relationship("MoodRecap", back_populates="user")