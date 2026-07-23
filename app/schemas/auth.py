"""Pydantic v2 schemas for authentication and user management."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserRegister(BaseModel):
    """Payload for user registration."""

    full_name: str = Field(..., min_length=1, max_length=255, description="User's full name")
    email: EmailStr = Field(..., description="Unique email address")
    password: str = Field(..., min_length=6, max_length=128, description="Plaintext password (hashed at rest)")
    state: str = Field(..., min_length=1, max_length=100, description="Nigerian state of residence")
    lga: str = Field(..., min_length=1, max_length=100, description="Local Government Area")
    age: int = Field(..., ge=0, le=120, description="Age in years")
    gender: Literal["Male", "Female", "Other"] = Field(..., description="Gender")
    phone_number: str | None = Field(default=None, max_length=20, description="Optional phone number")

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "full_name": "Ada Okonkwo",
            "email": "ada@example.com",
            "password": "strongpassword123",
            "state": "Lagos",
            "lga": "Ikeja",
            "age": 28,
            "gender": "Female",
            "phone_number": "+2348000000000",
        }
    })


class UserLogin(BaseModel):
    """Payload for user login."""

    email: EmailStr = Field(..., description="Registered email address")
    password: str = Field(..., description="Account password")

    model_config = ConfigDict(json_schema_extra={
        "example": {"email": "ada@example.com", "password": "strongpassword123"}
    })


class UserOut(BaseModel):
    """Public representation of a user."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str
    email: EmailStr
    state: str
    lga: str
    age: int
    gender: str
    phone_number: str | None
    role: str
    is_active: bool
    created_at: datetime


class Token(BaseModel):
    """JWT access + refresh token pair."""

    access_token: str = Field(..., description="Short-lived JWT access token")
    refresh_token: str = Field(..., description="Long-lived JWT refresh token")
    token_type: Literal["bearer"] = "bearer"


class RefreshRequest(BaseModel):
    """Payload for token refresh."""

    refresh_token: str = Field(..., description="A valid refresh JWT")

    model_config = ConfigDict(json_schema_extra={"example": {"refresh_token": "eyJhbGciOi..."}})


class TokenRefreshed(BaseModel):
    """Response after refreshing tokens."""

    access_token: str
    token_type: Literal["bearer"] = "bearer"


class MessageResponse(BaseModel):
    """Generic message response."""

    message: str
