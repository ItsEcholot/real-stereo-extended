import cv2


class Camera:
    def __init__(self, cameraId=0):
        self.exiting = False
        self.capture = cv2.VideoCapture(cameraId)
        self.on_frame = None

        if self.capture.isOpened() != True:
            raise RuntimeError('Camera with id ' +
                               str(cameraId) + ' is not available')

    def stop(self):
        self.exiting = True

    def process(self):
        try:
            while self.exiting == False:
                _, frame = self.capture.read()

                if self.on_frame != None:
                    self.send_frame(frame)
        finally:
            self.capture.release()

    def send_frame(self, frame):
        _, jpeg_frame = cv2.imencode('.jpg', frame)
        try:
            self.on_frame(jpeg_frame)
        except TypeError:
            self.on_frame = None
            print(
                'Error occurred in the on_frame callback, it will automatically get unregistered')

    def set_frame_callback(self, on_frame):
        self.on_frame = on_frame
