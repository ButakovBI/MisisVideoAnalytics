FROM python:3.10-slim AS builder

WORKDIR /app

COPY build/whl /whl

COPY source/backend/ /app

ARG LIBS
RUN pip3 install ${LIBS} --find-links /whl && rm -rf /whl
ENV PYTHONPATH=/app

CMD ["pytest", "-q"]