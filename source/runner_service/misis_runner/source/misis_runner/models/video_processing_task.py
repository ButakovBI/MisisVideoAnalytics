from dataclasses import dataclass
from uuid import UUID


@dataclass
class VideoProcessingTask:
    scenario_id: UUID
    video_path: str
    active: bool = True
