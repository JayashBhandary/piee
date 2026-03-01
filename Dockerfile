# ─────────────────────────────────────────────
# PIEE Backend — Multi-stage Dockerfile
# ─────────────────────────────────────────────

# ── Stage 1: Dependencies ───────────────────
FROM python:3.12-slim AS deps

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libffi-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── Stage 2: Runtime ────────────────────────
FROM python:3.12-slim AS runtime

WORKDIR /app

# Copy installed packages from deps stage
COPY --from=deps /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=deps /usr/local/bin /usr/local/bin

# Copy application code
COPY app/ ./app/
COPY prisma/ ./prisma/
COPY .env.example ./.env.example

# Generate Prisma client
RUN python3 -m prisma generate

# Healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python3 -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
