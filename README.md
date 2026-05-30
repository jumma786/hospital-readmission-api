# Hospital Readmission Risk API

A deployed machine-learning service that predicts **30-day hospital readmission risk** from patient features. Wraps the XGBoost model (AUC 0.907) from my [hospital-analytics-end-to-end](https://github.com/jumma786/hospital-analytics-end-to-end) project behind a FastAPI service, containerised with Docker, and deployed on Render.

**🔗 Live demo:** _to be added after deployment_ — `https://readmission-api.onrender.com/docs`

> Free-tier hosting sleeps when idle; the first request may take ~30–60 s to wake.

---

## What this demonstrates

- **Serving a trained model behind a REST API** with FastAPI
- **Production-correct feature handling** — the API accepts raw human-readable inputs and rebuilds the same `pd.get_dummies(drop_first=True)` encoding used at training time, then reindexes to the exact 26-column feature order. Unseen categories fall back to the reference category instead of crashing.
- **Input validation** with Pydantic (rejects malformed requests with a 422 and a clear error)
- **Request logging** for every call (method, path, status, latency) as the foundation for monitoring
- **Automated tests** with pytest covering health, prediction, validation, and edge cases
- **Containerised** with Docker for reproducible deployment
- **Deployed** on Render via a `render.yaml` Infrastructure-as-Code config

---

## Architecture

```
Client → FastAPI (/predict) → encoder rebuild → XGBoost (26 features) → risk score + label
                                                                          ↓
                                       request logger (method/path/status/latency)
```

Model and feature order are loaded **once at startup** (not per request) for low-latency inference.

---

## Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| `GET`  | `/`       | Service info |
| `GET`  | `/health` | Liveness check (used by Render) |
| `POST` | `/predict` | Predict 30-day readmission risk |
| `GET`  | `/docs`   | Interactive Swagger UI |

### Example request

```bash
curl -X POST https://readmission-api.onrender.com/predict \
  -H "Content-Type: application/json" \
  -d '{
    "patient_age": 78,
    "duration_hours": 1.0,
    "claim_cost": 146.18,
    "payer_coverage": 84.94,
    "prior_encounter_count": 0,
    "days_since_prev": null,
    "encounter_class": "emergency",
    "payer_name": "Medicare",
    "gender": "F",
    "race": "white"
  }'
```

### Example response

```json
{
  "readmission_probability": 0.7314,
  "risk_label": "high_risk"
}
```

---

## Run locally

```bash
# 1. Set up
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 2. Copy your trained model files into ./models/
#    (see models/README.md for the exact filenames)

# 3. Run the API
uvicorn app.main:app --reload
# → http://127.0.0.1:8000/docs

# 4. Run the tests
pytest -v
```

---

## Project structure

```
hospital-readmission-api/
├── app/
│   ├── main.py            # FastAPI app, endpoints, request logging
│   ├── model.py           # Model loading + encoding rebuild + prediction
│   └── schema.py          # Pydantic request/response validation
├── models/                # XGBoost model, feature order, input schema
├── tests/
│   └── test_api.py        # pytest suite
├── Dockerfile
├── render.yaml            # Render deployment config
├── requirements.txt
└── README.md
```

---

## Tech stack

- **ML** — XGBoost 3.2.0 (trained on Synthea synthetic EHR data, AUC 0.907)
- **API** — FastAPI 0.115, Pydantic 2.9
- **Serving** — Uvicorn ASGI server
- **Container** — Docker (Python 3.11-slim base)
- **Hosting** — Render (free tier)
- **Tests** — pytest + FastAPI TestClient

---

## Honest limitations

- **Synthetic training data.** The model was trained on Synthea-generated EHR records, not real clinical data. The AUC of 0.91 reflects the relative cleanliness of synthetic data; real-world 30-day readmission models typically achieve 0.65–0.75. **This service is not for clinical use.**
- **No retraining or drift detection.** Request logging is the foundation, but automated retraining triggers and drift monitoring are not implemented. They are the natural next step.
- **Free-tier hosting.** The service sleeps after 15 min idle and takes ~30–60 s to wake.
- **No authentication.** This is a portfolio demo; production deployment would add API keys and rate limiting.

---

## Related project

This service consumes the model trained in [**hospital-analytics-end-to-end**](https://github.com/jumma786/hospital-analytics-end-to-end), a four-phase project covering SQL Server data engineering, T-SQL analytics, Power BI dashboards, and the Python ML pipeline (with SHAP explainability).
