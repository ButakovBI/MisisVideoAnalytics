from contextlib import asynccontextmanager
from fastapi import FastAPI

from misis_scenario_api.kafka.producer import Producer
from misis_scenario_api.s3.s3_client import S3Client
from misis_scenario_api.database.database import engine
from misis_scenario_api.app.web.routers import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.s3_client = S3Client()
    app.state.kafka_producer = Producer()
    await app.state.kafka_producer.producer.start()

    async with engine.begin() as conn:
        await conn.run_sync(lambda sync_conn: sync_conn.execute("SELECT 1"))

    yield

    await app.state.kafka_producer.producer.stop()


def create_app() -> FastAPI:
    app = FastAPI(
        title="MISIS Scenario API",
        lifespan=lifespan
    )
    app.include_router(router)
    return app


app = create_app()
