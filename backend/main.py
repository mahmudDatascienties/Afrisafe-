from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.utils.model_loader import load_ml_models, clear_ml_models
from app.api import auth, prediction

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Lock/Load resources lokacin startup
    load_ml_models()
    yield
    # Cleanup resources lokacin shutdown
    clear_ml_models()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    lifespan=lifespan
)

# CORS Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(prediction.router, prefix="/api/v1/prediction", tags=["Prediction"])

@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "healthy", "service": settings.PROJECT_NAME}
