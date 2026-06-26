# syntax=docker/dockerfile:1
# ReYMeN Agent — Dockerfile
# Multi-stage build: builder → runtime

FROM python:3.11-slim AS builder

WORKDIR /build

# Build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy only dependency files first (layer caching)
COPY requirements.txt setup.py pyproject.toml ./

RUN pip install --user --no-cache-dir -r requirements.txt

# ── Runtime stage ──────────────────────────────────────────────────────────
FROM python:3.11-slim AS runtime

LABEL org.opencontainers.image.title="ReYMeN Agent"
LABEL org.opencontainers.image.description="Otonom AI asistan ve ajan sistemi"
LABEL org.opencontainers.image.version="0.1.0"

# System dependencies for Playwright + OCR
RUN apt-get update && apt-get install -y --no-install-recommends \
    libglib2.0-0 \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libdbus-1-3 \
    libxcb1 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2 \
    libatspi2.0-0 \
    libsqlite3-0 \
    tzdata \
    && rm -rf /var/lib/apt/lists/*

# Create app user (non-root)
RUN groupadd -r reymen && useradd -r -g reymen -d /app -s /sbin/nologin reymen

WORKDIR /app

# Copy Python packages from builder
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Copy application code
COPY --chown=reymen:reymen . .

# Playwright browsers (headless Chromium)
RUN python -m playwright install chromium --with-deps 2>/dev/null || true

# Runtime user
USER reymen

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD python -c "import reymen; print('OK')" || exit 1

# Default command
CMD ["python", "main.py"]
