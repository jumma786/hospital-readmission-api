"""FastAPI service exposing the readmission risk model."""

import logging
import time
from fastapi import FastAPI, Request
from app.schema import PatientFeatures, PredictionResponse
from app.model import predict

# --- Logging: this is your "monitoring awareness" layer -----------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger("readmission_api")

app = FastAPI(
    title="Hospital Readmission Risk API",
    description=(
        "Predicts 30-day hospital readmission risk from patient features "
        "(XGBoost, AUC 0.91 on synthetic Synthea EHR data). "
        "POST /predict with patient features to receive a risk score."
    ),
    version="1.0.0",
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration_ms = (time.time() - start) * 1000
    logger.info(
        f"{request.method} {request.url.path} -> {response.status_code} ({duration_ms:.1f}ms)"
    )
    return response


@app.get("/")
def root():
    return {
        "status": "ok",
        "service": "readmission-api",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health")
def health():
    """Liveness check used by Render to confirm the service is up."""
    return {"status": "healthy"}


@app.post("/predict", response_model=PredictionResponse)
def predict_readmission(features: PatientFeatures):
    """
    Predict 30-day readmission risk for a single patient encounter.
    Returns a probability (0.0 to 1.0) and a high_risk / low_risk label.
    """
    result = predict(features.model_dump())
    logger.info(
        f"Prediction: {result['risk_label']} "
        f"(p={result['readmission_probability']})"
    )
    return result
