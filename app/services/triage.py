"""Triage logic: maps model confidence into risk / recommendations."""

from __future__ import annotations

from typing import Any

from app.ml.model_service import predict as run_inference


def classify_risk(probability: float, symptoms: list[str]) -> str:
    """Return one of ``High``, ``Medium``, ``Low`` based on model probability.

    Symptoms act as a secondary clinical-safety boost: a single high-severity
    symptom can escalate risk one level, but only when the model already
    considers the case at least moderate. This keeps risk aligned with the
    model's actual estimate while still flagging severe presentations.
    """
    if probability >= 0.75:
        return "High"
    if probability >= 0.45:
        return "Medium"
    if "High Fever" in symptoms:
        return "Medium"
    return "Low"


def build_recommendation(risk: str, prediction: str) -> tuple[str, list[str]]:
    """Return ``(recommendation, advice)`` tailored to the risk level."""
    if risk == "High":
        recommendation = (
            "High risk detected. Visit the nearest health facility for malaria "
            "testing immediately. Severe symptoms require urgent clinical evaluation."
        )
        advice = [
            "Take a Rapid Diagnostic Test (RDT) or blood smear at a clinic.",
            "Begin prescribed antimalarial treatment (ACT) only after confirmation.",
            "Drink plenty of fluids and rest.",
            "Avoid self-medication or leftover antimalarials.",
            "Seek emergency care if confusion, seizures, or difficulty breathing occur.",
        ]
    elif risk == "Medium":
        recommendation = (
            "Moderate risk detected. Visit a clinic within 24-48 hours for a malaria test."
        )
        advice = [
            "Get a Rapid Diagnostic Test (RDT) to confirm malaria.",
            "Stay hydrated and monitor your temperature.",
            "Use insecticide-treated bed nets.",
            "Do not self-medicate; wait for test results.",
        ]
    else:
        recommendation = (
            "Low risk indicators. Monitor symptoms and rest. Seek care if symptoms worsen."
        )
        advice = [
            "Rest and maintain hydration.",
            "Continue monitoring for fever or new symptoms.",
            "Use preventive measures (bed nets, repellents).",
            "Visit a clinic if symptoms persist beyond 48 hours.",
        ]
    return recommendation, advice


def build_ai_insights(
    prediction: str, probability: float, risk: str, payload: dict[str, Any]
) -> str:
    """Produce a short, human-readable explanation of the model's reasoning."""
    symptoms = payload.get("symptoms", [])
    symptom_text = ", ".join(symptoms) if symptoms else "no significant symptoms"
    pct = round(probability * 100, 1)

    if prediction == "Malaria":
        lead = (
            f"The model estimates a {pct}% probability of malaria based on the "
            f"reported symptom profile ({symptom_text})."
        )
    else:
        lead = (
            f"The model estimates a low ({pct}%) probability of malaria. Reported "
            f"symptoms ({symptom_text}) do not strongly match the malaria profile."
        )

    notes: list[str] = []
    if payload.get("mosquito_exposure"):
        notes.append("Recent mosquito bites increase epidemiological likelihood.")
    if payload.get("travel_history"):
        notes.append("Recent travel to endemic areas is a supporting risk factor.")
    if payload.get("drug_history"):
        notes.append("Recent antimalarial use may suppress test results; inform your clinician.")

    return f"{lead} {' '.join(notes)}".strip()


def triage_assessment(payload: dict[str, Any]) -> dict[str, Any]:
    """Run inference and assemble the full triage result dict.

    The returned dict matches :class:`app.schemas.prediction.PredictionResponse`
    (minus ``timestamp``, which is added by the service layer).
    """
    raw = run_inference(payload)
    probability = raw["probability"]
    prediction = raw["prediction"]
    symptoms = list(payload.get("symptoms", []))

    risk = classify_risk(probability, symptoms)
    recommendation, advice = build_recommendation(risk, prediction)

    return {
        "prediction": prediction,
        "confidence": raw["confidence"],
        "risk": risk,
        "recommendation": recommendation,
        "advice": advice,
        "symptoms": payload,
        "ai_insights": build_ai_insights(prediction, probability, risk, payload),
    }
