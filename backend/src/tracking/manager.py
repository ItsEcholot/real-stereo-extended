from threading import Thread
from .camera import Camera


class TrackingManager:
    def __init__(self):
        self.camera = None
        self.thread = None

    def start_tracking(self):
        self.camera = Camera(1)
        self.thread = Thread(target=self.camera.process)
        self.thread.start()

    def stop_tracking(self):
        self.camera.stop()
        self.thread.join()

    def set_frame_callback(self, on_frame):
        if self.camera == None:
            raise RuntimeError('Tracking is not available')

        self.camera.set_frame_callback(on_frame)
