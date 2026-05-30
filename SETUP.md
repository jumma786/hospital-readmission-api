# Setup Guide — Build, Test, Deploy

Step-by-step instructions to take this starter from zero to a live URL on Render.
Expected outputs are stated upfront so you know when a step worked.

---

## STEP 0 — Copy your model artefacts

**Expected output:** three files in `models/`.

From your training notebook's `models/` folder, copy these three files into the `models/` folder of this project:

- `readmission_xgb.json`
- `feature_order.json`
- `input_schema.json`

**Sanity check (from a terminal in the project root):**
```bash
ls models/
# Should show:  README.md  feature_order.json  input_schema.json  readmission_xgb.json
```

If any file is missing, the API will fail to start. Re-run the Step 1 cell in your notebook to regenerate them.

---

## STEP 1 — Create the virtual environment

**Expected output:** an activated `.venv` prompt prefix like `(.venv)`.

```bash
python -m venv .venv

# Activate it:
#   Windows (PowerShell):  .venv\Scripts\Activate.ps1
#   Windows (CMD):         .venv\Scripts\activate.bat
#   Mac/Linux:             source .venv/bin/activate
```

Confirm Python version:
```bash
python --version
# Should be 3.11 or 3.12 (matches the Dockerfile base)
```

---

## STEP 2 — Install dependencies

**Expected output:** all packages installed without errors.

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

> First install takes a couple of minutes — XGBoost and pandas are large wheels.

Verify XGBoost installed at the right version:
```bash
python -c "import xgboost; print(xgboost.__version__)"
# Should print:  3.2.0
```

---

## STEP 3 — Run the API locally

**Expected output:** a server at `http://127.0.0.1:8000` and a working Swagger UI at `/docs`.

```bash
uvicorn app.main:app --reload
```

You should see log lines like:
```
INFO:     Will watch for changes in these directories: ['...']
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started server process [...]
INFO:     Application startup complete.
```

Open **http://127.0.0.1:8000/docs** in your browser.

1. Expand `POST /predict`
2. Click **Try it out**
3. The example payload is pre-filled (real values from your training data)
4. Click **Execute**

Expected response:
```json
{
  "readmission_probability": 0.xxxx,
  "risk_label": "low_risk" or "high_risk"
}
```

🎉 If you see that, your model is live locally.

Stop the server with `Ctrl+C`.

---

## STEP 4 — Run the tests

**Expected output:** `7 passed`.

```bash
pytest -v
```

You should see seven tests pass:
- `test_root_returns_service_info`
- `test_health_returns_healthy`
- `test_predict_returns_valid_score`
- `test_predict_handles_first_encounter_null`
- `test_predict_rejects_bad_age`
- `test_predict_rejects_missing_field`
- `test_predict_handles_unseen_category_gracefully`

If any test fails: paste the full error output and the test name — we'll debug it.

---

## STEP 5 — (Optional) Test the Docker container

**Expected output:** same `/docs` page works, served from inside a container.

Only if you have Docker Desktop installed and running:

```bash
docker build -t readmission-api .
docker run -p 8000:8000 readmission-api
```

Visit `http://localhost:8000/docs`. Same result, but now it's running inside the exact environment Render will use. Stop with `Ctrl+C`.

Skip this step if you don't have Docker — Render will build the container itself when you deploy.

---

## STEP 6 — Push to GitHub

**Expected output:** a public repo `jumma786/hospital-readmission-api`.

```bash
git init
git add .
git commit -m "Deployable readmission risk API (FastAPI + XGBoost + Docker)"
```

On GitHub, create an empty public repo named `hospital-readmission-api` (no README — you have one). Then:

```bash
git remote add origin https://github.com/jumma786/hospital-readmission-api.git
git branch -M main
git push -u origin main
```

> Important: the `models/` folder contains your trained model JSON. Free-tier model files are small, so committing them is fine. If your models grow large later, switch to Git LFS or fetch them from object storage at container startup.

---

## STEP 7 — Deploy on Render

**Expected output:** a live URL like `https://readmission-api.onrender.com`.

1. Go to **render.com** and sign up with your GitHub account (free, no credit card needed for the free web service tier).
2. **New → Web Service**
3. Connect your GitHub and pick the `hospital-readmission-api` repo.
4. Render detects the `Dockerfile` and `render.yaml` automatically.
5. Choose the **Free** plan.
6. Click **Create Web Service**.

Watch the build logs. First build takes 3–5 minutes (pulling the Python image, installing dependencies, copying the model).

When you see **"Your service is live 🎉"** and a URL, open `https://<your-url>.onrender.com/docs` and test the `/predict` endpoint.

> First request after idle is slow (~30–60s) because the free tier sleeps. This is documented in the README as a known free-tier limitation, not a bug.

---

## STEP 8 — Final polish

After the service is live, update the **README.md**:

1. Replace the "🔗 Live demo: _to be added after deployment_" line with your actual Render URL.
2. Commit and push:
   ```bash
   git add README.md
   git commit -m "Add live demo URL"
   git push
   ```
3. (Optional) Add a screenshot of the Swagger UI to the README — recruiters love a visual.

---

## What to say in interviews

> "I took my hospital readmission model and deployed it as a containerised FastAPI service on Render — with input validation, request logging, and automated tests. The API accepts raw inputs and recreates the same encoding used at training time, so it handles unseen categories gracefully. It's live; you can hit the endpoint. I haven't built retraining or drift detection yet, but the logging layer is the foundation I'd extend for that."

That's honest, specific, and turns your one real gap into a strength.

---

## When something breaks

Almost certainly one of these:

1. **`uvicorn` says "ModuleNotFoundError: No module named 'app'"**
   You're not in the project root. `cd` into the folder that contains the `app/` directory.

2. **`FileNotFoundError: models/readmission_xgb.json`**
   You forgot Step 0. Copy the three model files into `models/`.

3. **`ImportError` related to xgboost on Render**
   Render's logs will show it — usually a version mismatch. Check `requirements.txt` pins `xgboost==3.2.0`.

4. **Render build hangs or fails**
   Open the build logs in Render's dashboard. Paste the failing line and I'll debug it with you.

5. **Tests fail with model loading error**
   Same root cause as #2 — model files not in `models/`.

Don't grind on errors alone. Paste the exact error message and the step number, and we'll fix it.
