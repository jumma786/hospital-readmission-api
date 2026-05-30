"""
End-to-end API tests using FastAPI's TestClient.

These tests prove:
  - The service comes up and reports healthy
  - The /predict endpoint returns a valid probability + label
  - Input validation rejects malformed requests with 422
  - A "first encounter" (days_since_prev = None) is handled correctly
"""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

VALID_PAYLOAD = {
    "patient_age": 78,
    "duration_hours": 1.0,
    "claim_cost": 146.18,
    "payer_coverage": 84.94,
    "prior_encounter_count": 0,
    "days_since_prev": None,
    "encounter_class": "emergency",
    "payer_name": "Medicare",
    "gender": "F",
    "race": "white",
}


def test_root_returns_service_info():
    r = client.get("/")
    assert r.status_code == 200
    assert r.json()["service"] == "readmission-api"


def test_health_returns_healthy():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "healthy"}


def test_predict_returns_valid_score():
    r = client.post("/predict", json=VALID_PAYLOAD)
    assert r.status_code == 200
    body = r.json()
    assert 0.0 <= body["readmission_probability"] <= 1.0
    assert body["risk_label"] in ("high_risk", "low_risk")


def test_predict_handles_first_encounter_null():
    """days_since_prev=None should be silently replaced with the 9999 sentinel."""
    payload = {**VALID_PAYLOAD, "days_since_prev": None, "prior_encounter_count": 0}
    r = client.post("/predict", json=payload)
    assert r.status_code == 200


def test_predict_rejects_bad_age():
    payload = {**VALID_PAYLOAD, "patient_age": 999}
    r = client.post("/predict", json=payload)
    assert r.status_code == 422


def test_predict_rejects_missing_field():
    payload = {k: v for k, v in VALID_PAYLOAD.items() if k != "patient_age"}
    r = client.post("/predict", json=payload)
    assert r.status_code == 422


def test_predict_handles_unseen_category_gracefully():
    """An unseen category should fall back to the reference (all dummies = 0), not crash."""
    payload = {**VALID_PAYLOAD, "race": "some_unseen_value"}
    r = client.post("/predict", json=payload)
    assert r.status_code == 200
