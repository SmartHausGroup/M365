# syntax=docker/dockerfile:1.7-labs

ARG PYTHON_VERSION=3.12

FROM python:${PYTHON_VERSION}-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1
WORKDIR /app

# Builder to install deps
FROM base AS builder
RUN apt-get update && apt-get install -y --no-install-recommends build-essential && rm -rf /var/lib/apt/lists/*
COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install --upgrade pip && pip wheel --wheel-dir /wheels .

# Runtime image
FROM base AS runtime
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates && rm -rf /var/lib/apt/lists/*
COPY --from=builder /wheels /wheels
RUN pip install --no-index --find-links=/wheels smarthaus-m365 && rm -rf /wheels

# Copy runtime assets
COPY templates ./templates
COPY static ./static

# Healthcheck port env
ENV PORT=8000

# Entrypoint to allow dynamic port
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Non-root user
RUN useradd -m -u 10001 appuser && mkdir -p /app/data /app/logs /app/config && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD python -c "import os,sys,urllib.request,json; p=os.getenv('PORT','8000');\
  \n\
  \n d=urllib.request.urlopen(f'http://127.0.0.1:{p}/health',timeout=2).read();\
  \n\
  \n import json as _j; sys.exit(0 if _j.loads(d).get('status')=='ok' else 1)" || exit 1

ENTRYPOINT ["/entrypoint.sh"]
CMD ["uvicorn", "provisioning_api.main:app", "--host", "0.0.0.0", "--port", "8000"]

