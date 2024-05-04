import cv2
from managers import WindowManager, CaptureManager
from datetime import datetime


class Cameo:
    def __init__(self):
        self._window_manager = WindowManager(
            window_name="Cameo", key_press_callback=self.on_key_press
        )
        self._capture_manager = CaptureManager(
            capture=cv2.VideoCapture(0),
            preview_window_manger=self._window_manager,
            should_mirror_preview=True,
        )

    # @staticmethod
    def run(self):
        """Run the main loop."""
        self._window_manager.create_window()
        while self._window_manager.is_window_created:
            self._capture_manager.enter_frame()
            frame = self._capture_manager.frame

            self._capture_manager.exit_frame()
            self._window_manager.process_events()

    def on_key_press(self, keycode):
        """Handle a keypress.
        space  -> Take a screenshot.
        tab    -> Start/stop recording a screencast.
        escape -> Quit.
        """
        if keycode == 32:  # space
            self._capture_manager.write_image(
                filename=f"media/screenshots/screenshot{datetime.now():%Y-%m-%d_%H:%M:%S}.png"
            )
        elif keycode == 9:  # tab
            if not self._capture_manager.is_writing_video:
                self._capture_manager.start_writing_video(
                    filename=f"media/screenrecords/screen_record_{datetime.now():%Y-%m-%d_%H:%M:%S}.avi"
                )
            else:
                self._capture_manager.stop_writing_video()
        elif keycode == 27:  # escape
            self._window_manager.destroy_window()


if __name__ == "__main__":
    Cameo().run()
