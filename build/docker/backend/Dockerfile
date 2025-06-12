FROM python:3.10-slim AS builder

RUN groupadd -r appgroup  && \
    useradd -r -g appgroup appuser && \
    mkdir -p /app && \
    chown appuser:appgroup /app

WORKDIR /app

COPY --chown=appuser:appgroup build/whl /whl
COPY --chown=appuser:appgroup source/backend/ /app

ARG LIBS
RUN pip3 install --no-cache-dir ${LIBS} --find-links /whl && \
    rm -rf /whl && \
    rm -rf /root/.cache/pip

ENV PYTHONPATH=/app

HEALTHCHECK --interval=30s --timeout=3s \
    CMD curl -f http://localhost:8000/docs || exit 1

USER appuser

CMD ["uvicorn", "misis_api.source.main:app", "--host", "0.0.0.0", "--port", "8000"]