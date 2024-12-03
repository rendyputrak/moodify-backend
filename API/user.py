from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session 
from pydantic import BaseModel
from typing import Annotated
from models import User
from database import get_db
from passlib.context import CryptContext

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

class UserCreate(BaseModel):
    Email: str
    Password: str
    Firstname: str = None
    Lastname: str = None
    Gender: str = None
    BirthDate: str = None
    Avatar: str = None

class UserUpdate(BaseModel):
    Firstname: str = None
    Lastname: str = None
    Gender: str = None
    BirthDate: str = None
    Avatar: str = None

class PasswordUpdate(BaseModel):
    old_password: str
    new_password: str

class LoginRequest(BaseModel):
    email: str
    password: str

# Endpoint untuk menambah user / signup
@router.post("/signup/", status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, db: Annotated[Session, Depends(get_db)]):
    try:
        if len(user.Password) < 8:
            raise HTTPException(status_code=400, detail="Password minimal 8 karakter")

        hashed_password = pwd_context.hash(user.Password)
        db_user = User(
            Email=user.Email,
            Password=hashed_password,
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

# Endpoint untuk edit profil
@router.put("/users/{user_id}/profile", status_code=status.HTTP_200_OK)
async def update_profile(user_id: int, user_update: UserUpdate, db: Annotated[Session, Depends(get_db)]):
    user = db.query(User).filter(User.UserID == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User tidak ditemukan!")

    if user_update.Firstname:
        user.Firstname = user_update.Firstname
    if user_update.Lastname:
        user.Lastname = user_update.Lastname
    if user_update.Gender:
        user.Gender = user_update.Gender
    if user_update.BirthDate:
        user.BirthDate = user_update.BirthDate
    if user_update.Avatar:
        user.Avatar = user_update.Avatar

    db.commit()
    db.refresh(user)
    return {"message": "Profil berhasil diperbarui", "user": user}

# Endpoint untuk login
@router.post("/login", status_code=status.HTTP_200_OK)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.Email == request.email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Email tidak ditemukan")
    
    if not pwd_context.verify(request.password, user.Password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Password salah")
    
    return {"message": "Login berhasil!", "user_id": user.UserID, "email": user.Email}

# Endpoint untuk ganti password
# @router.put("/users/{user_id}/password", status_code=status.HTTP_200_OK)
# async def update_password(user_id: int, password_update: PasswordUpdate, db: Annotated[Session, Depends(get_db)]):
#     user = db.query(User).filter(User.UserID == user_id).first()
#     if not user:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User tidak ditemukan!")
    
#     if not pwd_context.verify(password_update.old_password, user.Password):
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Password lama salah")
 
#     if len(password_update.new_password) < 8:
#         raise HTTPException(status_code=400, detail="Password minimal 8 karakter")

#     user.Password = pwd_context.hash(password_update.new_password)
#     db.commit()
#     return {"message": "Password berhasil diperbarui"}