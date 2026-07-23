"""Schemas package."""

from app.schemas.admin import (
    AdminPredictionOut,
    AdminUserOut,
    StatisticsResponse,
)
from app.schemas.auth import (
    MessageResponse,
    RefreshRequest,
    Token,
    TokenRefreshed,
    UserLogin,
    UserOut,
    UserRegister,
)
from app.schemas.prediction import (
    PredictionHistoryItem,
    PredictionHistoryList,
    PredictionRequest,
    PredictionResponse,
)

__all__ = [
    "AdminPredictionOut",
    "AdminUserOut",
    "StatisticsResponse",
    "MessageResponse",
    "RefreshRequest",
    "Token",
    "TokenRefreshed",
    "UserLogin",
    "UserOut",
    "UserRegister",
    "PredictionHistoryItem",
    "PredictionHistoryList",
    "PredictionRequest",
    "PredictionResponse",
]
