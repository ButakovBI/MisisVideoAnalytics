import cv2

FRAME_SKIP = 10
SIZE = (640, 480)


class VideoProcessor:
    def __init__(self, scenario_id: str, video_path: str):
        self.scenario_id = scenario_id
        self.video_path = video_path
        self._break_flag = False
        self.last_processed_frame = 0

    async def process(self, frame_callback):
        cap = cv2.VideoCapture(self.video_path)

        while not self._break_flag and cap.isOpened():
            ret, frame = cap.read()
            self.last_processed_frame += 1

            if not ret or (self.last_processed_frame % FRAME_SKIP != 0):
                continue

            processed_frame = self._preprocess(frame)
            await frame_callback(processed_frame)
        cap.release()

    def _preprocess(self, frame):
        return cv2.resize(frame, SIZE) / 255.0

    def stop(self):
        self._break_flag = True
