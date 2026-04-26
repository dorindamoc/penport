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
        print("[watcher] started")
        while not self._stop_event.is_set():
            self._scan()
            interval = self._cfg["pipeline"].get("poll_interval_seconds", 300)
            print(f"[watcher] next scan in {interval}s — use Sync Now to scan immediately")
            self._trigger_event.wait(timeout=interval)
            self._trigger_event.clear()
        print("[watcher] stopped")

    def trigger_now(self) -> None:
        print("[watcher] manual trigger")
        self._trigger_event.set()

    def stop(self) -> None:
        self._stop_event.set()
        self._trigger_event.set()

    def reload_config(self, cfg: dict) -> None:
        self._cfg = cfg

    def _scan(self) -> None:
        inbox = Path(self._cfg["folders"]["inbox"]).expanduser()
        print(f"[watcher] scanning {inbox}")

        if not inbox.exists():
            print(f"[watcher] inbox does not exist: {inbox}")
            return

        queued = 0
        for path in sorted(inbox.iterdir()):
            if path.suffix.lower() not in _IMAGE_EXTENSIONS:
                continue
            if tracker.is_processed(str(path)):
                print(f"[watcher] skipping already-processed: {path.name}")
                continue
            print(f"[watcher] queuing: {path.name}")
            self._job_queue.put(path)
            queued += 1

        print(f"[watcher] scan done — {queued} job(s) queued")
