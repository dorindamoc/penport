from __future__ import annotations

import queue
import threading
from pathlib import Path

import tracker

_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".heic", ".webp"}


class Watcher(threading.Thread):
    def __init__(self, cfg: dict, job_queue: queue.Queue) -> None:
        super().__init__(daemon=True, name="PenportWatcher")
        self._cfg = cfg
        self._job_queue = job_queue
        self._stop_event = threading.Event()
        self._trigger_event = threading.Event()

    def run(self) -> None:
        interval = self._cfg["pipeline"].get("poll_interval_seconds", 300)
        while not self._stop_event.is_set():
            self._scan()
            # Wait for the interval or an early trigger
            self._trigger_event.wait(timeout=interval)
            self._trigger_event.clear()

    def trigger_now(self) -> None:
        self._trigger_event.set()

    def stop(self) -> None:
        self._stop_event.set()
        self._trigger_event.set()  # unblock the wait

    def reload_config(self, cfg: dict) -> None:
        self._cfg = cfg

    def _scan(self) -> None:
        inbox = Path(self._cfg["folders"]["inbox"]).expanduser()
        if not inbox.exists():
            return
        for path in sorted(inbox.iterdir()):
            if path.suffix.lower() not in _IMAGE_EXTENSIONS:
                continue
            if tracker.is_processed(str(path)):
                continue
            self._job_queue.put(path)
