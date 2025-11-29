from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app import models, database, auth
from pydantic import BaseModel
from typing import Optional
import logging
import traceback

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/auth",
    tags=["authentication"],
)

class UserCreate(BaseModel):
    username: str
    password: str
    full_name: Optional[str] = None
    provider_info: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    username: str
    full_name: Optional[str] = None
    provider_info: Optional[str] = None

    class Config:
        orm_mode = True


@router.post("/register")
def register(user: UserCreate, db: Session = Depends(database.get_db)):
    try:
        # Basic validation
        if not user.username or not user.password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username and password are required"
            )

        print("RAW PASSWORD LENGTH:", len(user.password))

        # Check if user exists
        existing_user = db.query(models.User).filter(models.User.username == user.username).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )

        # ✅ Hash password (pbkdf2_sha256, no 72-byte limit)
        try:
            hashed_password = auth.get_password_hash(user.password)
        except Exception as hash_error:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Password hashing error: {hash_error}"
            )

        # Create new user record
        new_user = models.User(
            username=user.username,
            hashed_password=hashed_password,
            full_name=user.full_name,
            provider_info=user.provider_info
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return {
            "id": new_user.id,
            "username": new_user.username,
            "full_name": new_user.full_name,
            "provider_info": new_user.provider_info,
            "message": "User registered successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        try:
            db.rollback()
        except:
            pass
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}"
        )


@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
def read_users_me(current_user: models.User = Depends(auth.get_current_user)):
    return current_user
