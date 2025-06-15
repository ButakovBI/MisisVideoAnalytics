import json
import logging
import threading
from confluent_kafka import Consumer

from misis_orchestrator.app.event_handler import EventHandler
from misis_orchestrator.app.command_handler import CommandHandler


class KafkaConsumer:
    def __init__(self, bootstrap_servers: str, group_id: str,
                 event_handler: EventHandler, command_handler: CommandHandler):
        self.consumer = Consumer({
            'bootstrap.servers': bootstrap_servers,
            'group.id': group_id,
            'auto.offset.reset': 'earliest'
        })
        self.event_handler = event_handler
        self.command_handler = command_handler
        self._stop_event = threading.Event()

    def start(self):
        self.consumer.subscribe(['scenario_commands', 'heartbeats', 'predictions'])
        self.thread = threading.Thread(target=self._consume, daemon=True)
        self.thread.start()
        self._logger().info("Kafka consumer started")

    def stop(self):
        self._stop_event.set()
        self.consumer.close()
        self.thread.join()
        self._logger().info("Kafka consumer stopped")

    def _consume(self):
        while not self._stop_event.is_set():
            msg = self.consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                self._logger().error(f"Consumer error: {msg.error()}")
                continue

            try:
                data = json.loads(msg.value().decode('utf-8'))
                topic = msg.topic()

                if topic == 'scenario_commands':
                    self._handle_command(data)
                elif topic == 'heartbeats':
                    self._handle_heartbeat(data)
                elif topic == 'predictions':
                    self._handle_prediction(data)

            except Exception as e:
                self._logger().error(f"Error processing message: {e}")

    def _handle_command(self, data):
        command = data.get('command')
        scenario_id = data.get('scenario_id')

        if command == 'create':
            video_path = data.get('video_path')
            self.command_handler.create_scenario(video_path)
        elif command == 'start':
            self.command_handler.start_scenario(scenario_id)
        elif command == 'stop':
            self.command_handler.stop_scenario(scenario_id)

    def _handle_heartbeat(self, data):
        scenario_id = data.get('scenario_id')
        timestamp = data.get('timestamp')
        self.event_handler.handle_heartbeat(scenario_id, timestamp)

    def _handle_prediction(self, data):
        scenario_id = data.get('scenario_id')
        frame_number = data.get('frame_number')
        boxes = data.get('boxes')
        self.event_handler.handle_prediction(scenario_id, frame_number, boxes)

    def _logger(self):
        return logging.getLogger(__name__)
