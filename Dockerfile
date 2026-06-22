# Builds the Flask backend from the monorepo root (Railway default context).
FROM python:3.12-slim-bookworm

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=100

COPY zomato_recommendation/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY zomato_recommendation/ ./

# Bake a compact parquet (~550 KB) so runtime stays under Railway's RAM limit.
RUN python scripts/bake_dataset.py

CMD ["/bin/sh", "-c", "exec gunicorn --bind 0.0.0.0:${PORT:-8080} --workers 1 --threads 2 --timeout 120 --access-logfile - --error-logfile - api:app"]
