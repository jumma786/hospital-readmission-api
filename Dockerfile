FROM python:3.11-slim

WORKDIR /code

# Install Python deps first (better Docker layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Then copy the app and model artefacts
COPY ./app ./app
COPY ./models ./models

# Render sets $PORT at runtime; default to 8000 locally.
ENV PORT=8000

CMD uvicorn app.main:app --host 0.0.0.0 --port $PORT
