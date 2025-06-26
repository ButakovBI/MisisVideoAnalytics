FROM python:3.10-slim AS builder

RUN groupadd -r appgroup  && \
    useradd -r -g appgroup appuser && \
    mkdir -p /app && \
    chown appuser:appgroup /app

WORKDIR /app

COPY --chown=appuser:appgroup build/whl /whl
COPY --chown=appuser:appgroup source/inference_service/ /app

ARG LIBS
RUN pip install --no-cache-dir misis_inference --find-links /whl/ && \
    apt-get update && apt-get install -y libgl1 libglib2.0-0 && \
    rm -rf /root/.cache/pip

ENV PYTHONPATH=/app

HEALTHCHECK --interval=30s --timeout=3s \
    CMD curl -f http://localhost:8001/docs || exit 1

USER appuser

CMD ["uvicorn", "misis_inference.app.web.app:app", "--host", "0.0.0.0", "--port", "8001"]
