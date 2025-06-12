FROM python:3.10-slim AS builder

WORKDIR /app

COPY build/whl /whl

COPY source/backend/ /app

ARG LIBS
RUN pip3 install ${LIBS} --find-links /whl && rm -rf /whl

CMD ["uvicorn", "misis_api.source.main:app", "--host", "0.0.0.0", "--port", "8000"]