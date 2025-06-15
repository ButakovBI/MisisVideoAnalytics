import os
import logging

from fastapi import FastAPI

from misis_healthcheck.heartbeat.heartbeat_processor import HeartbeatProcessor
from misis_healthcheck.watchdog import Watchdog
from misis_orchestrator.database.database import Database
from misis_orchestrator.app.command_handler import CommandHandler
from misis_orchestrator.app.event_handler import EventHandler
from misis_orchestrator.kafka.kafka_consumer import KafkaConsumer
from misis_orchestrator.kafka.kafka_producer import KafkaProducer
from misis_orchestrator.health.health_storage import DatabaseHealthStorage

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    app = FastAPI(title="MISIS Scenario Orchestrator")

    db_connection = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@postgres/analytics")
    kafka_bootstrap = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")

    db = Database(db_connection)
    kafka_producer = KafkaProducer(kafka_bootstrap)
    command_handler = CommandHandler(db)
    event_handler = EventHandler(db)

    kafka_consumer = KafkaConsumer(
        bootstrap_servers=kafka_bootstrap,
        group_id="orchestrator",
        event_handler=event_handler,
        command_handler=command_handler
    )
    kafka_consumer.start()

    health_storage = DatabaseHealthStorage(db)
    heartbeat_processor = HeartbeatProcessor(health_storage)
    watchdog = Watchdog(
        storage=health_storage,
        check_interval=10,
        heartbeat_timeout=30
    )

    def restart_scenario(scenario_id):
        command_handler.start_scenario(scenario_id)
        logger.info(f"Restarted scenario {scenario_id} due to heartbeat timeout")

    watchdog.add_callback(restart_scenario)
    watchdog.start()

    app.state.db = db
    app.state.kafka_producer = kafka_producer
    app.state.command_handler = command_handler
    app.state.event_handler = event_handler
    app.state.kafka_consumer = kafka_consumer
    app.state.heartbeat_processor = heartbeat_processor
    app.state.watchdog = watchdog

    return app


app = create_app()


@app.on_event("shutdown")
def shutdown_event():
    logger.info("Shutting down Orchestrator service")
    app.state.kafka_consumer.stop()
    app.state.watchdog.stop()
    logger.info("Kafka consumer and watchdog stopped")
