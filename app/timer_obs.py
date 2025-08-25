import threading
import time


class TimerController:
    def __init__(self, total_seconds, update_ui_callback, finish_callback):
        self.total_seconds = total_seconds
        self.remaining_seconds = total_seconds
        self.update_ui_callback = update_ui_callback
        self.finish_callback = finish_callback
        self.running = False
        self.thread = None

    def start(self):
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False

    def _run(self):
        while self.running and self.remaining_seconds > 0:
            self.update_ui_callback(self.remaining_seconds, self.total_seconds)
            time.sleep(1)
            self.remaining_seconds -= 1

        if self.running:
            self.running = False
            self.finish_callback()
