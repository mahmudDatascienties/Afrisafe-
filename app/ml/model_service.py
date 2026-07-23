"""Machine-learning model loading and inference.

The exported LogisticRegression model was trained on 17 features::

    age, fever, high_fever, headache, chills, vomiting, duration,
    gender_Male, state_Enugu, state_FCT, state_Kaduna, state_Kano,
    state_Katsina, state_Lagos, state_Oyo, state_Rivers, state_Sokoto

The frontend sends a higher-level payload (free-form symptom labels, a state
name, gender, age, duration, and exposure flags). This module bridges the two
representations. The model is loaded exactly once at startup (singleton).
"""

from __future__ import annotations

import logging
from typing import Any

import joblib
import numpy as np

from app.config.settings import settings
from app.core.exceptions import AppException

logger = logging.getLogger("afrisafe.ml")

# Symptom labels from the frontend -> model binary feature columns.
SYMPTOM_TO_FEATURE: dict[str, str] = {
    "fever": "fever",
    "high fever": "high_fever",
    "headache": "headache",
    "chills": "chills",
    "vomiting": "vomiting",
}

# States the model was trained on. Any other state is encoded as all-zeros
# (the model's implicit "other" baseline).
KNOWN_STATES: set[str] = {
    "Enugu", "FCT", "Kaduna", "Kano", "Katsina", "Lagos", "Oyo", "Rivers", "Sokoto",
}

# Map frontend state names to the encoded column suffix used by the model.
STATE_ALIASES: dict[str, str] = {
    "Abuja (FCT)": "FCT",
    "FCT": "FCT",
}


class MLModel:
    """Singleton holder for the loaded model and its feature names."""

    _instance: "MLModel | None" = None

    def __new__(cls) -> "MLModel":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.model = None  # type: ignore[attr-defined]
            cls._instance.feature_names = []  # type: ignore[attr-defined]
            cls._instance.loaded = False  # type: ignore[attr-defined]
        return cls._instance

    def load(self) -> None:
        """Load model + feature names from disk. Safe to call once at startup."""
        try:
            self.model = joblib.load(settings.MODEL_PATH)
            logger.info("Loaded malaria model from %s", settings.MODEL_PATH)
        except Exception as exc:
            logger.exception("Failed to load malaria model")
            raise AppException(
                status_code=500,
                detail=f"Failed to load malaria model: {exc}",
                error_code="MODEL_LOAD_ERROR",
            ) from exc

        try:
            self.feature_names = list(joblib.load(settings.FEATURE_NAMES_PATH))
            logger.info(
                "Loaded %d feature names from %s",
                len(self.feature_names),
                settings.FEATURE_NAMES_PATH,
            )
        except Exception as exc:
            logger.exception("Failed to load feature names")
            raise AppException(
                status_code=500,
                detail=f"Failed to load feature names: {exc}",
                error_code="MODEL_LOAD_ERROR",
            ) from exc

        self.loaded = True


def get_model() -> MLModel:
    """Return the singleton :class:`MLModel`, loading it if necessary."""
    model = MLModel()
    if not model.loaded:
        model.load()
    return model


def build_feature_vector(payload: dict[str, Any]) -> np.ndarray:
    """Translate a frontend assessment payload into a model feature vector.

    The vector is ordered exactly as ``MLModel.feature_names`` and contains a
    single row (shape ``(1, n_features)``).
    """
    model = get_model()
    features: dict[str, Any] = {name: 0 for name in model.feature_names}

    # Numeric features
    features["age"] = int(payload.get("age", 0))
    features["duration"] = int(payload.get("duration", 1))

    # Gender -> gender_Male (1 if Male else 0)
    if "gender_Male" in features:
        features["gender_Male"] = 1 if str(payload.get("gender", "")).lower() == "male" else 0

    # Symptoms -> binary columns
    symptoms = [str(s).strip().lower() for s in payload.get("symptoms", [])]
    for label, col in SYMPTOM_TO_FEATURE.items():
        if col in features:
            features[col] = 1 if label in symptoms else 0

    # State -> one-hot columns (state_<NAME>)
    raw_state = str(payload.get("state", "")).strip()
    state_key = STATE_ALIASES.get(raw_state, raw_state)
    state_col = f"state_{state_key}"
    if state_col in features and state_key in KNOWN_STATES:
        features[state_col] = 1

    return np.array([[features[name] for name in model.feature_names]], dtype=float)


def predict(payload: dict[str, Any]) -> dict[str, Any]:
    """Run inference for ``payload`` and return a raw result dict.

    Keys returned: ``prediction``, ``probability``, ``confidence``.
    Higher-level triage (risk / recommendation / advice) is derived by
    :mod:`app.services.triage`.
    """
    vector = build_feature_vector(payload)
    model = get_model()

    try:
        proba = model.model.predict_proba(vector)[0]
    except Exception as exc:
        logger.exception("Model prediction failed")
        raise AppException(
            status_code=500,
            detail="Prediction failed",
            error_code="PREDICTION_ERROR",
        ) from exc

    # classes_ is [0, 1]; index 1 == "Malaria positive".
    positive_index = list(model.model.classes_).index(1)
    positive_proba = float(proba[positive_index])

    prediction = "Malaria" if positive_proba >= 0.5 else "No Malaria"
    confidence = round(
        positive_proba * 100 if positive_proba >= 0.5 else (1 - positive_proba) * 100, 2
    )

    return {
        "prediction": prediction,
        "probability": positive_proba,
        "confidence": confidence,
    }
