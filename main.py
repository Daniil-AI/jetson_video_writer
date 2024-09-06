import os
import time
import threading
from datetime import datetime
import cv2
import numpy as np
import keyboard

class VideoRecorder:
    """Class for recording video using OpenCV."""

    def __init__(
        self,
        name: str = "temp_video.mp4",
        fourcc: str = "mp4v",
        camindex: int = 0,
        fps: int = 20,
    ) -> None:

        self.video_filename: str = name
        self.device_index: int = camindex
        self.fourcc: str = fourcc
        self.video_cap: cv2.VideoCapture = cv2.VideoCapture(self.device_index)
        self.video_writer: int = cv2.VideoWriter_fourcc(*self.fourcc)

        self.fps: int = fps
        sizey, sizex = self.video_cap.read()[1].shape[:2]
        self.frame_size: tuple[int, int] = (sizex, sizey)
        self.video_out: cv2.VideoWriter = cv2.VideoWriter(
            self.video_filename, self.video_writer, self.fps, self.frame_size
        )

        self.__frame_counts: int = 0
        self.start_time: float = time.time()
        self.timer_current: float = 0.0

        self.__open: bool = True
        self.video_thread: threading.Thread | None = None

    def record(self) -> None:
        """Start recording video."""

        while self.__open:
            ret: bool
            video_frame: np.ndarray
            ret, video_frame = self.video_cap.read()

            if ret:
                if video_frame.shape[2] != 3:
                    print("Warning: Frame does not have 3 channels (RGB).")
                    break

                self.record_status()
                self.video_out.write(video_frame)
                print(f"Frame shape: {video_frame.shape}")                    

            else:
                print("Error: Failed to capture video frame.")
                break
        self.cleanup()

    def record_status(self) -> None:
        "Input counter read frames and mean FPS"
        self.timer_current = time.time() - self.start_time
        self.__frame_counts += 1
        print(
            f"{self.__frame_counts} frames written in {self.timer_current:.2f} seconds"
        )
        print(f"Mean FPS: {self.__frame_counts / self.timer_current:.2f}")

    def stop(self) -> None:
        """Stop recording video and join the thread."""
        self.__open = False
        if self.video_thread is not None:
            self.video_thread.join()

    def start(self) -> None:
        """Start video recording in a separate thread."""
        self.video_thread = threading.Thread(target=self.record)
        self.video_thread.start()

    def cleanup(self) -> None:
        """Release resources and close windows."""
        if self.video_out.isOpened():
            self.video_out.release()
        if self.video_cap.isOpened():
            self.video_cap.release()
        cv2.destroyAllWindows()


def get_video_path() -> str:
    """Generate a directory path based on the current datetime."""
    current_datetime: str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    current_dir: str = os.path.join(os.getcwd(), current_datetime)
    if not os.path.exists(current_dir):
        os.mkdir(current_dir)
    return current_dir


if __name__ == "__main__":
    # MEAN_TIME_RECORDING = 5  # Duration recording session in seconds
    CURENT_DIR: str = get_video_path()

    number_video: int = 0
    while True:
        video = VideoRecorder(
            name=f"{CURENT_DIR}/video_{number_video}.mp4", fourcc="mp4v", fps = 20
        )
        video.start()
        # time.sleep(MEAN_TIME_RECORDING)
        
        event = keyboard.read_event()
        video.stop()
        number_video += 1
