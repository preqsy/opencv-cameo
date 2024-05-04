import cv2 as cv
import numpy as np
import time


class CaptureManager:
    def __init__(self, capture, preview_window_manger=None, should_mirror_preview=True):
        self.preview_window_manger = preview_window_manger
        self.should_mirror_preview = should_mirror_preview
        self._capture = capture
        self._channel = 0
        self._entered_frame = False
        self._frame = None
        self._image_filename = None
        self._video_filename = None
        self._video_encoding = None
        self._video_writer = None
        self._start_time = None
        self._frame_elapsed = 0
        self._fps_estimate = None

    @property
    def channel(self) -> None:
        return self._channel

    @channel.setter
    def channel(self, value):
        if self._channel != value:
            self._channel = value
            self._frame = None

    @property
    def frame(self):
        if self._entered_frame and self._frame is None:
            _, self._frame = self._capture.retrieve()
        return self._frame

    @property
    def is_writing_image(self):
        return self._image_filename is not None

    @property
    def is_writing_video(self):
        return self._video_filename is not None

    def enter_frame(self):
        """Capture Next Frame If Any."""
        # But first, check that any previous frame was exited.

        assert (
            not self._entered_frame
        ), "previous entered_frame() had no matching exit_frame()"

        if self._capture is not None:
            self._entered_frame = self._capture.grab()

    def exit_frame(self):
        """Draw to the window. Write to files. Release the
        frame."""
        # Check whether any grabbed frame is retrievable.
        # The getter may retrieve and cache the frame.
        if self.frame is None:
            self._entered_frame = False
            return
        # Update the FPS estimate and related variables.
        if self._frame_elapsed == 0:
            self._start_time = time.time()
        else:
            time_elapsed = time.time() - self._start_time
            self._fps_estimate = self._frame_elapsed / time_elapsed
        self._frame_elapsed += 1
        # draw window if any
        if self.preview_window_manger is not None:
            if self.should_mirror_preview:
                mirrored_frame = np.fliplr(self._frame).copy()
                self.preview_window_manger.show(mirrored_frame)
            else:
                self.preview_window_manger.show(self._frame)
        if self.is_writing_image:
            cv.imwrite(self._image_filename, self._frame)
            self._image_filename = None

        # write to video if any
        self._write_video_frame()

        # Release the frame.
        self._frame = None
        self._entered_frame = False

    def write_image(self, filename):
        """Write the next exited frame to an image file."""
        self._image_filename = filename

    def start_writing_video(
        self, filename, encoding=cv.VideoWriter_fourcc("I", "4", "2", "0")
    ):
        """Start writing exited frames to a video file."""
        self._video_filename = filename
        self._video_encoding = encoding

    def stop_writing_video(self):
        """Stop writing exited frames to a video file."""
        self._video_filename = None
        self._video_encoding = None
        self._video_writer = None

    def _write_video_frame(self):
        if not self.is_writing_video:
            return
        if self._video_writer is None:
            fps = self._capture.get(cv.CAP_PROP_FPS)
            if fps == 0.0:
                # The capture's FPS is unknown so use an estimate.
                if self._frame_elapsed < 20:
                    # Wait until more frames elapse so that the
                    # estimate is more stable.
                    return
                else:
                    fps = self._fps_estimate
            size = (
                int(self._capture.get(cv.CAP_PROP_FRAME_WIDTH)),
                int(self._capture.get(cv.CAP_PROP_FRAME_HEIGHT)),
            )
            self._video_writer = cv.VideoWriter(
                self._video_filename, self._video_encoding, fps, size
            )
        self._video_writer.write(self._frame)


class WindowManager:

    def __init__(self, window_name, key_press_callback=None):
        self.key_press_callback = key_press_callback
        self._window_name = window_name
        self._is_window_created = False

    @property
    def is_window_created(self):
        return self._is_window_created

    def create_window(self):
        cv.namedWindow(self._window_name)
        self._is_window_created = True

    def show(self, frame):
        cv.imshow(self._window_name, frame)

    def destroy_window(self):
        cv.destroyWindow(self._window_name)
        self._is_window_created = False

    def process_events(self):
        keycode = cv.waitKey(1)
        if self.key_press_callback is not None and keycode != -1:
            # Discard any non-ASCII info encoded by GTK.
            keycode &= 0xFF
            self.key_press_callback(keycode)
