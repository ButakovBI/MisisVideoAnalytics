from enum import StrEnum


class KafkaTopic(StrEnum):
    HEARTBEATS = "heartbeats"
    SCENARIO_EVENTS = "scenario_events"
    RUNNER_COMMANDS = "runner_commands"
