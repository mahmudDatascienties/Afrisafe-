from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


class PatientData(BaseModel):
    age: int = Field(..., ge=0, le=120, description="Patient age in years")
    gender: str = Field(..., description="Gender (Male, Female, Other)")
    state: str = Field(..., min_length=2, max_length=100, description="State of residence")
    lga: Optional[str] = Field(default="", max_length=100, description="Local Government Area")

    @field_validator("gender")
    @classmethod
    def validate_gender(cls, value: str) -> str:
        clean_gender = value.strip().title()
        if clean_gender not in ["Male", "Female", "Other"]:
            raise ValueError("Gender must be 'Male', 'Female', or 'Other'.")
        return clean_gender

    @field_validator("state", "lga")
    @classmethod
    def sanitize_strings(cls, value: str) -> str:
        return value.strip()


class AssessmentData(BaseModel):
    symptoms: List[str] = Field(..., min_length=1, description="List of present symptoms")
    durationDays: int = Field(..., ge=1, le=90, description="Duration of symptoms in days")
    recentMosquitoBites: bool = Field(default=False)
    recentTravel: bool = Field(default=False)
    takenMalariaDrugs: bool = Field(default=False)

    @field_validator("symptoms")
    @classmethod
    def validate_symptoms(cls, symptoms_list: List[str]) -> List[str]:
        cleaned = [s.strip() for s in symptoms_list if s.strip()]
        if not cleaned:
            raise ValueError("At least one valid symptom must be selected.")
        return cleaned


class PredictionRequest(BaseModel):
    patient: PatientData
    assessment: AssessmentData


class PredictionResponse(BaseModel):
    prediction: str = Field(..., example="Positive")
    risk: str = Field(..., example="High")
    confidence: float = Field(..., example=94.7)
    recommendation: str = Field(
        ..., 
        example="Visit the nearest health facility for malaria testing immediately."
    )
    advice: List[str] = Field(
        ...,
        example=[
            "Drink enough water.",
            "Do not self-medicate.",
            "Take a Rapid Diagnostic Test."
        ]
    )
