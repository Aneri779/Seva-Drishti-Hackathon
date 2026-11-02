# ================================================================
# SAR-Drishti Backend – Python 3.11 + GDAL + Pango
# ================================================================
FROM python:3.11-slim-bookworm AS base

# System dependencies: GDAL, Pango (WeasyPrint PDF), git, curl
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ make \
    gdal-bin libgdal-dev libgeos-dev libproj-dev \
    libpq-dev \
    libpango-1.0-0 libpangoft2-1.0-0 libpangocairo-1.0-0 \
    libcairo2 libffi-dev \
    git curl wget \
    && rm -rf /var/lib/apt/lists/*

ENV GDAL_VERSION=3.6 \
    CPLUS_INCLUDE_PATH=/usr/include/gdal \
    C_INCLUDE_PATH=/usr/include/gdal \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# ── Python deps ─────────────────────────────────────────────────
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ── App source (secrets excluded via .dockerignore) ─────────────
COPY app/ ./app/
COPY alembic/ ./alembic/
COPY alembic.ini .
COPY scripts/ ./scripts/
COPY templates/ ./templates/

# ── Non-root user ────────────────────────────────────────────────
RUN useradd -m -u 1000 sardrishti && chown -R sardrishti /app
USER sardrishti

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", \
     "--workers", "2", "--loop", "uvloop", "--http", "h11"]
