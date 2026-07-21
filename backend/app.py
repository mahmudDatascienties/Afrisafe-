from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers.prediction import router as prediction_router
from utils.model_loader import ml_model


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Load the machine learning model once when the API starts.
    """
    ml_model.load()
    print("✅ Malaria model loaded successfully.")

    yield

    print("🛑 API shutting down.")


app = FastAPI(
    title="Malaria Symptom Triage Helper API",
    description=(
        "AI-powered malaria symptom triage API for early risk assessment. "
        "This tool is for screening only and is NOT a medical diagnosis."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# Allow frontend applications to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routes
app.include_router(prediction_router)


@app.get("/", tags=["System"])
async def root():
    """
    Root endpoint.
    """
    return {
        "application": "Malaria Symptom Triage Helper API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health", tags=["System"])
async def health():
    """
    Health check endpoint.
    """
    return {
        "status": "healthy",
        "model_loaded": ml_model.model is not None
    }
