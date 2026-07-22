import numpy as np
from app.utils.model_loader import get_model
from app.schemas.prediction import SymptomAssessmentRequest, PredictionResult

class PredictionService:
    @staticmethod
    def predict_malaria(payload: SymptomAssessmentRequest) -> PredictionResult:
        model = get_model("malaria_model")
        
        # Prepare feature vector base on trained order
        features = [
            payload.fever,
            payload.headache,
            payload.chills,
            payload.fatigue,
            payload.nausea,
            payload.joint_pain,
            payload.age,
            payload.duration_days
        ]
        
        # Calculate prediction probability
        prob = model.predict_proba([features])[0][1] if hasattr(model, "predict_proba") else float(model.predict([features])[0])
        has_malaria = prob >= 0.5
        
        # Assign risk levels
        if prob < 0.3:
            risk_level = "Low"
            recommendations = ["Monitor symptoms", "Stay hydrated"]
        elif prob < 0.7:
            risk_level = "Moderate"
            recommendations = ["Visit a local clinic for RDT (Rapid Diagnostic Test)", "Get adequate rest"]
        else:
            risk_level = "High"
            recommendations = ["Seek immediate medical attention at the nearest hospital", "Do not self-medicate"]

        return PredictionResult(
            has_malaria=has_malaria,
            risk_score=round(float(prob), 2),
            risk_level=risk_level,
            recommendations=recommendations
        )
