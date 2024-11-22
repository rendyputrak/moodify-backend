from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session 
from database import engine, SessionLocal  
from pydantic import BaseModel, validator
from typing import List, Annotated
from models import User
from database import get_db

router = APIRouter()

class UserCreate(BaseModel):
    Email: str
    Password: str
    Firstname: str = None
    Lastname: str = None
    Gender: str = None
    BirthDate: str = None
    Avatar: str = None

# Endpoint untuk menambah user
@router.post("/users/", status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, db: Annotated[Session, Depends(get_db)]):
    try:
        if len(user.Password) < 8:
            raise HTTPException(status_code=400, detail="Password minimal 8 karakter")

        db_user = User(
            Email=user.Email,
            Password=user.Password,
            Firstname=user.Firstname,
            Lastname=user.Lastname,
            Gender=user.Gender,
            BirthDate=user.BirthDate
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
    
# Endpoint untuk mendapatkan semua user
@router.get("/users/", status_code=status.HTTP_200_OK)
async def get_users(db: Annotated[Session, Depends(get_db)]):
    return db.query(User).all()
    
# Endpoint untuk mendapatkan user berdasar id
@router.get("/users/{user_id}", status_code=status.HTTP_200_OK)
async def get_users(user_id: int, db: Annotated[Session, Depends(get_db)]):
    user = db.query(User).filter(User.UserID == user_id).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User tidak ditemukan!")
    return user

# @router.post("/login/")
# async def login(email: str, password: str, db: Annotated[Session, Depends(get_db)]):
#     db_user = db.query(models.User).filter(models.User.Email == email).first()
#     if db_user and db_user.verify_password(password):
#         return {"message": "Login berhasil!"}
#     raise HTTPException(status_code=401, detail="Invalid credentials")