import logging
import threading
import time
from datetime import datetime, timedelta
from misis_healthcheck.abstract_storage import HeartbeatStorage


class Watchdog(threading.Thread):
    def __init__(self,
                 storage: HeartbeatStorage,
                 check_interval: int = 10,
                 heartbeat_timeout: int = 30):
        super().__init__(daemon=True)
        self.storage = storage
        self.check_interval = check_interval
        self.heartbeat_timeout = heartbeat_timeout
        self._stop_event = threading.Event()
        self._callbacks = []

    def add_callback(self, callback):
        self._callbacks.append(callback)

    def stop(self):
        self._stop_event.set()

    def run(self):
        self._logger().info("Watchdog started")
        while not self._stop_event.is_set():
            try:
                self._check_heartbeats()
            except Exception as e:
                self._logger().error(f"Watchdog error: {e}")
            time.sleep(self.check_interval)
        self._logger().info("Watchdog stopped")

    def _check_heartbeats(self):
        now = datetime.utcnow()
        active_scenarios = self.storage.get_active_scenarios()

        for scenario in active_scenarios:
            last_heartbeat = self.storage.get_last_heartbeat(scenario.id)
            if not last_heartbeat:
                self._logger().warning(f"No heartbeat ever received for scenario {scenario.id}")
                continue

            if (now - last_heartbeat) > timedelta(seconds=self.heartbeat_timeout):
                self._logger().warning(f"Heartbeat timeout for scenario {scenario.id}")
                for callback in self._callbacks:
                    try:
                        callback(scenario.id)
                    except Exception as e:
                        self._logger().error(f"Callback error for scenario {scenario.id}: {e}")

    def _logger(self):
        return logging.getLogger(__name__)
