from enum import StrEnum


class KafkaTopic(StrEnum):
    HEARTBEATS = "heartbeats"
    RUNNER_COMMANDS = "runner_commands"
