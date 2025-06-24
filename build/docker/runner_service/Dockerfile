FROM python:3.10-slim AS builder

RUN groupadd -r appgroup  && \
    useradd -r -g appgroup appuser && \
    mkdir -p /app && \
    chown appuser:appgroup /app

WORKDIR /app

COPY --chown=appuser:appgroup build/whl /whl
COPY --chown=appuser:appgroup source/runner_service/ /app

ARG LIBS
RUN pip install --no-cache-dir ${LIBS} --find-links /whl/ && \
    rm -rf /root/.cache/pip

ENV PYTHONPATH=/app

USER appuser

CMD ["python", "-m", "misis_runner.main.main"]
