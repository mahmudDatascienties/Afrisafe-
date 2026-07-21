from typing import Literal

from pydantic import BaseModel, Field


class PredictionResponse(BaseModel):
    """
    Response schema returned after prediction.
    """

    prediction: Literal["Malaria", "No Malaria"] = Field(
        ...,
        description="Predicted class"
    )

    probability: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Prediction probability"
    )

    urgency: Literal["Low", "Medium", "High"] = Field(
        ...,
        description="Risk level"
    )

    recommendation: str = Field(
        ...,
        description="Medical recommendation"
    )
