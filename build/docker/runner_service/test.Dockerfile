FROM python:3.10-slim AS builder

WORKDIR /app

COPY build/whl /whl

COPY source/runner_service/ /app

ARG LIBS
RUN pip3 install --no-cache-dir ${LIBS} --find-links /whl && \
    rm -rf /root/.cache/pip

ENV PYTHONPATH=/app

CMD ["pytest", "-q"]
