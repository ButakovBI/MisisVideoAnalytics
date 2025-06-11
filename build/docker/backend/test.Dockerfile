FROM python:3.10-slim AS builder
WORKDIR /app

COPY build/docker/images_configuration.json /app/images_configuration.json
COPY build/docker/get_config.py /app/get_config.py

RUN pip install --no-cache-dir $(python3 /app/get_config.py /app/images_configuration.json test_backend LIBS)

COPY source/backend/setup.py /app/setup.py
COPY source/backend/pyproject.toml /app/pyproject.toml
COPY source/backend/source /app/source
COPY source/backend/tests /app/tests
RUN pip install --no-cache-dir /app


FROM python:3.10-slim
WORKDIR /app

COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /app /app

ENV PYTHONPATH=/app

CMD ["pytest", "-q"]