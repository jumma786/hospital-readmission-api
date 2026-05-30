"""
Loads the trained XGBoost readmission model and runs predictions.

The API accepts raw human-readable inputs (e.g. encounter_class="emergency").
This module re-applies the SAME one-hot encoding that was used at training time
(pd.get_dummies with drop_first=True) and reindexes to the exact 26-column
feature order the model expects. Categories the model never saw map to 0,
which correctly treats them as the reference/dropped category.
"""

import json
from pathlib import Path
import pandas as pd
import xgboost as xgb

MODEL_DIR = Path(__file__).resolve().parent.parent / "models"

# ---- Load once at startup (NOT per request — that would be slow) -------------
_model = xgb.XGBClassifier()
_model.load_model(str(MODEL_DIR / "readmission_xgb.json"))

with open(MODEL_DIR / "feature_order.json") as f:
    TRAINED_FEATURES: list[str] = json.load(f)   # 26 columns, exact training order

with open(MODEL_DIR / "input_schema.json") as f:
    SCHEMA = json.load(f)

NUMERIC_FEATURES = SCHEMA["numeric_features"]              # 6 numerics
CATEGORICAL_FEATURES = SCHEMA["categorical_features"]      # 4 categoricals
NULL_SENTINEL = SCHEMA["days_since_prev_null_sentinel"]    # 9999


def _build_feature_row(raw_input: dict) -> pd.DataFrame:
    """
    Take a dict of raw API inputs, return a 1-row DataFrame with EXACTLY the
    26 columns the model was trained on, in the correct order.
    """
    # 1. Apply the same null-handling rule used at training time.
    if raw_input.get("days_since_prev") is None:
        raw_input["days_since_prev"] = NULL_SENTINEL

    # 2. Build a one-row DataFrame from the raw input.
    row = pd.DataFrame([raw_input])

    # 3. Apply the SAME encoding step as training:
    #    pd.get_dummies(..., drop_first=True) on the 4 categorical columns.
    row_encoded = pd.get_dummies(
        row,
        columns=CATEGORICAL_FEATURES,
        drop_first=True,
    )

    # 4. Reindex to the exact trained feature order.
    #    - Columns the model expects but aren't in this row -> filled with 0
    #      (this is correct: 0 = "this category not present")
    #    - Columns in this row that the model never saw -> dropped
    #      (e.g. a brand-new race category will simply have all race dummies = 0,
    #       which treats it as the dropped reference category — sensible default)
    row_aligned = row_encoded.reindex(columns=TRAINED_FEATURES, fill_value=0)

    return row_aligned


def predict(raw_input: dict) -> dict:
    """Return readmission probability and a high/low risk label."""
    features = _build_feature_row(raw_input)
    proba = float(_model.predict_proba(features)[0, 1])
    label = "high_risk" if proba >= 0.5 else "low_risk"
    return {
        "readmission_probability": round(proba, 4),
        "risk_label": label,
    }
