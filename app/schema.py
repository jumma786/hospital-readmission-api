"""Pydantic schemas for request/response validation."""

from typing import Optional
from pydantic import BaseModel, Field


class PatientFeatures(BaseModel):
    # ---- Numeric features ----
    patient_age: float = Field(..., ge=0, le=120, description="Patient age in years")
    duration_hours: float = Field(..., ge=0, description="Encounter duration in hours")
    claim_cost: float = Field(..., ge=0, description="Total claim cost")
    payer_coverage: float = Field(..., ge=0, description="Amount covered by payer")
    prior_encounter_count: int = Field(..., ge=0, description="Prior encounters for this patient")
    days_since_prev: Optional[float] = Field(
        None, ge=0,
        description="Days since previous encounter. Leave null/None for a patient's first encounter."
    )

    # ---- Categorical features (free-text — model handles unseen categories) ----
    encounter_class: str = Field(..., description="e.g. emergency, inpatient, outpatient, ambulatory, wellness")
    payer_name: str = Field(..., description="e.g. Medicare, Medicaid, NO_INSURANCE, Humana")
    gender: str = Field(..., description="F or M")
    race: str = Field(..., description="e.g. white, black, asian, hawaiian, native, other")

    model_config = {
        "json_schema_extra": {
            "example": {
                "patient_age": 78,
                "duration_hours": 1.0,
                "claim_cost": 146.18,
                "payer_coverage": 84.94,
                "prior_encounter_count": 0,
                "days_since_prev": None,
                "encounter_class": "emergency",
                "payer_name": "Medicare",
                "gender": "F",
                "race": "white"
            }
        }
    }


class PredictionResponse(BaseModel):
    readmission_probability: float
    risk_label: str
