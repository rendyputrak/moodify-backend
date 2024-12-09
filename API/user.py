import os
import shutil
from fastapi import APIRouter, HTTPException, Depends, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Annotated
from models import User
from database import get_db
from passlib.context import CryptContext
from dotenv import load_dotenv
import jwt
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer, OAuth2
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.openapi.models import OAuth2 as OAuth2Model

load_dotenv()

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = os.getenv("SECRET_KEY", "secret_key")  # Use environment variable for secret key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # Set the expiration time for the access token

# OAuth2PasswordBearer instance
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login/")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# JWT token generation
def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# JWT token verification
def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

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

class PasswordUpdate(BaseModel):
    old_password: str
    new_password: str

class LoginRequest(BaseModel):
    email: str
    password: str

# Endpoint for signup
@router.post("/signup/", status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, db: Annotated[Session, Depends(get_db)]):
    try:
        existing_user = db.query(User).filter(User.Email == user.Email).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")

        if len(user.Password) < 8:
            raise HTTPException(status_code=400, detail="Password must be at least 8 characters")

        hashed_password = hash_password(user.Password)
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

# Endpoint for login and token creation
@router.post("/login/", status_code=status.HTTP_200_OK)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.Email == request.email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Email not found")

    if not verify_password(request.password, user.Password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect password")

    access_token = create_access_token(data={"sub": str(user.UserID)})
    return {"access_token": access_token, "token_type": "bearer"}

# Dependency to get the current user from the token
def get_current_user(token: str = Depends(oauth2_scheme)):
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return verify_token(token)

# Endpoint to get user profile with authentication
@router.get("/users/{user_id}", status_code=status.HTTP_200_OK)
async def get_user_profile(
    user_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: dict = Depends(get_current_user)
):
    if str(user_id) != str(current_user.get("sub")):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this profile"
        )
    user = db.query(User).filter(User.UserID == user_id).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return {
        "UserID": user.UserID,
        "Email": user.Email,
        "Firstname": user.Firstname,
        "Lastname": user.Lastname,
        "Gender": user.Gender,
        "BirthDate": user.BirthDate,
        "Avatar": user.Avatar,
    }

# Endpoint to update user profile with authentication
@router.put("/users/{user_id}/profile", status_code=status.HTTP_200_OK)
async def update_profile(
    user_id: int,
    user_update: UserUpdate,
    db: Annotated[Session, Depends(get_db)],
    Avatar: Annotated[UploadFile | None, File()] = None,
    current_user: dict = Depends(get_current_user)
):
    if str(user_id) != str(current_user.get("sub")):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this profile")

    user = db.query(User).filter(User.UserID == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Update data pengguna
    if user_update.Firstname:
        user.Firstname = user_update.Firstname
    if user_update.Lastname:
        user.Lastname = user_update.Lastname
    if user_update.Gender:
        user.Gender = user_update.Gender
    if user_update.BirthDate:
        user.BirthDate = user_update.BirthDate

    # Upload dan validasi avatar
    if Avatar:
        if Avatar.content_type not in ["image/jpeg", "image/png"]:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid avatar format")
        upload_dir = f"./media/uploads/avatars/user_{user_id}"
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, Avatar.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(Avatar.file, buffer)
        user.Avatar = file_path

    db.commit()
    db.refresh(user)

    return {
        "message": "Profile updated successfully",
        "user": {
            "UserID": user.UserID,
            "Firstname": user.Firstname,
            "Lastname": user.Lastname,
            "Gender": user.Gender,
            "BirthDate": user.BirthDate,
            "Avatar": user.Avatar,
        }
    }

# Endpoint for updating password
@router.put("/users/{user_id}/password", status_code=status.HTTP_200_OK)
async def update_password(
    user_id: int,
    password_update: PasswordUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: dict = Depends(get_current_user)
):
    if str(user_id) != str(current_user.get("sub")):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this password")

    user = db.query(User).filter(User.UserID == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if not verify_password(password_update.old_password, user.Password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect old password. Please try again."
        )

    if len(password_update.new_password) < 8 or " " in password_update.new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be at least 8 characters and not contain spaces"
        )

    user.Password = hash_password(password_update.new_password)
    db.commit()

    return {"message": "Password updated successfully"}


# Endpoint to delete user account and related data
@router.delete("/users/{user_id}", status_code=status.HTTP_200_OK)
async def delete_user_account(
    user_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: dict = Depends(get_current_user)
):
    if str(user_id) != str(current_user.get("sub")):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this account")

    # Get the user record
    user = db.query(User).filter(User.UserID == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Delete user profile picture (avatar)
    if user.Avatar and os.path.exists(user.Avatar):
        os.remove(user.Avatar)

    # Delete the user record
    db.delete(user)
    db.commit()

    return {"message": "Account and related data deleted successfully"}
