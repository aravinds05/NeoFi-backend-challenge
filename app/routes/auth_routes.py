import sys
sys.path.append("../")
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta

from auth.utils import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
)
from database import get_db
from schemas import UserCreate, Token, LoginRequest, RegisterRequest, TokenData
from models import User

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

ACCESS_TOKEN_EXPIRE_MINUTES = 30
# new user registeration 
@router.post("/register", response_model=Token)
def register_user(user_data: RegisterRequest, db: Session = Depends(get_db)):
    user_exists = db.query(User).filter(User.email == user_data.email).first()
    if user_exists:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_pw = get_password_hash(user_data.password)
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_pw,
        role=user_data.role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    access_token = create_access_token(
        data={"sub": new_user.email},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    refresh_token = create_refresh_token(data={"sub": new_user.email})
    return {"access_token": access_token, "token_type": "bearer", "refresh_token": refresh_token}


# login
@router.post("/login", response_model=Token)
def login_user(login_data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == login_data.email).first()
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    refresh_token = create_refresh_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer", "refresh_token": refresh_token}


# refresh token
@router.post("/refresh", response_model=Token)
def refresh_token(token_data: TokenData):
    if not token_data.email:
        raise HTTPException(status_code=400, detail="Invalid refresh request")

    access_token = create_access_token(
        data={"sub": token_data.email},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    refresh_token = create_refresh_token(data={"sub": token_data.email})
    return {"access_token": access_token, "token_type": "bearer", "refresh_token": refresh_token}

@router.post("/logout")
def logout_user():
    return {"message": "Successfully logged out"}