"""Pydantic v2 schemas for the malaria prediction feature."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class PredictionRequest(BaseModel):
    """Payload accepted by the prediction endpoint.

    Mirrors the frontend assessment form. ``symptoms`` is a free-form list of
    human-readable symptom labels that the ML service maps onto the model's
    binary feature columns.
    """

    age: int = Field(..., ge=0, le=120, description="Patient age in years")
    gender: Literal["Male", "Female", "Other"] = Field(..., description="Patient gender")
    state: str = Field(..., min_length=1, max_length=100, description="Nigerian state")
    lga: str | None = Field(default=None, max_length=100, description="Local Government Area")
    symptoms: list[str] = Field(
        default_factory=list,
        description="Symptom labels, e.g. ['Fever', 'High Fever', 'Headache', 'Chills', 'Vomiting']",
    )
    duration: int = Field(..., ge=1, le=14, description="Symptom duration in days")
    mosquito_exposure: bool = Field(default=False, description="Recent mosquito bites")
    travel_history: bool = Field(default=False, description="Recent travel to endemic areas")
    drug_history: bool = Field(default=False, description="Recent antimalarial use")

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "age": 25,
            "gender": "Male",
            "state": "Kano",
            "lga": "Nassarawa",
            "symptoms": ["High Fever", "Headache", "Chills"],
            "duration": 3,
            "mosquito_exposure": True,
            "travel_history": False,
            "drug_history": False,
        }
    })


class PredictionResponse(BaseModel):
    """Structured prediction result returned to the client."""

    prediction: str = Field(..., description="'Malaria' or 'No Malaria'")
    confidence: float = Field(..., ge=0.0, le=100.0, description="Model confidence percentage")
    risk: str = Field(..., description="Triage risk level: Low, Medium, or High")
    recommendation: str = Field(..., description="Tailored clinical recommendation")
    advice: list[str] = Field(..., description="Actionable advice items")
    symptoms: dict[str, Any] = Field(..., description="Echo of the input payload")
    timestamp: datetime = Field(..., description="Prediction timestamp")

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "prediction": "Malaria",
            "confidence": 87.5,
            "risk": "High",
            "recommendation": "Visit the nearest health facility immediately.",
            "advice": ["Take a Rapid Diagnostic Test (RDT).", "Begin ACT after confirmation."],
            "symptoms": {"age": 25, "gender": "Male", "state": "Kano", "symptoms": ["High Fever"]},
            "timestamp": "2026-07-23T09:00:00Z",
        }
    })


class PredictionHistoryItem(BaseModel):
    """A single prediction history record."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    prediction: str
    confidence: float
    risk: str
    recommendation: str
    advice: list[Any]
    symptoms: dict[str, Any]
    created_at: datetime


class PredictionHistoryList(BaseModel):
    """Paginated prediction history response."""

    total: int
    items: list[PredictionHistoryItem]
