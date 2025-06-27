FROM python:3.10-slim AS builder

RUN groupadd -r appgroup  && \
    useradd -r -g appgroup appuser && \
    mkdir -p /app && \
    chown appuser:appgroup /app

WORKDIR /app

COPY --chown=appuser:appgroup build/whl /whl
COPY --chown=appuser:appgroup source/api_service/ /app

ARG LIBS
RUN pip3 config set global.index-url https://mirrors.sustech.edu.cn/pypi/simple && \
    pip3 install --default-timeout=3000 --retries=10 --no-cache-dir misis_scenario_api --find-links /whl/ && \
    rm -rf /root/.cache/pip

ENV PYTHONPATH=/app

HEALTHCHECK --interval=30s --timeout=3s \
    CMD curl -f http://localhost:8000/docs || exit 1

USER appuser

CMD ["uvicorn", "misis_scenario_api.app.web.app:app", "--host", "0.0.0.0", "--port", "8000"]
