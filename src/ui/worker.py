from PySide6.QtCore import QThread, Signal
from PIL import Image


class _Cancelled(Exception):
    """Raised inside on_progress to abort processing."""


class FilterWorker(QThread):
    progress     = Signal(int, int)   # (pixels_done, pixels_total)
    result_ready = Signal(object)     # PIL Image (or None on error)

    def __init__(self, fn, args=(), kwargs=None, parent=None):
        super().__init__(parent)
        self._fn        = fn
        self._args      = tuple(args)
        self._kwargs    = dict(kwargs or {})
        self._cancelled = False

    def cancel(self):
        self._cancelled = True

    def run(self):
        def on_progress(done: int, total: int):
            if self._cancelled:
                raise _Cancelled()
            self.progress.emit(done, total)

        try:
            result = self._fn(*self._args, on_progress=on_progress, **self._kwargs)
        except _Cancelled:
            return
        except Exception as e:
            print(f"[FilterWorker] Processing error: {e}")
            result = None

        if not self._cancelled:
            self.result_ready.emit(result)
