from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.auth import UserRegister, UserLogin, Token, UserResponse
from app.schemas.response import APIEnvelope
from app.services.auth_service import AuthService

router = APIRouter()

@router.post("/register", response_model=APIEnvelope[UserResponse], status_code=status.HTTP_201_CREATED)
def register(payload: UserRegister, db: Session = Depends(get_db)):
    user = AuthService.register_user(db, payload)
    return APIEnvelope(
        success=True,
        message="User registered successfully",
        data=UserResponse.model_validate(user)
    )

@router.post("/login", response_model=APIEnvelope[Token])
def login(payload: UserLogin, db: Session = Depends(get_db)):
    token = AuthService.authenticate_user(db, payload)
    return APIEnvelope(
        success=True,
        message="Login successful",
        data=Token(access_token=token)
    )
