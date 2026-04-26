from __future__ import annotations

import queue
import sys

import wx

import tracker
from config import config_exists, load_config
from settings_window import SettingsWindow
from tray import TrayIcon, WorkerThread
from watcher import Watcher


def main() -> None:
    tracker.init_db()
    first_run = not config_exists()
    cfg = load_config()

    app = wx.App(False)
    app.SetAppName("Penport")

    job_queue: queue.Queue = queue.Queue()

    tray = TrayIcon(cfg, job_queue)
    watcher = Watcher(cfg, job_queue)
    worker = WorkerThread(cfg, job_queue, tray)

    tray.attach_watcher(watcher)

    watcher.start()
    worker.start()

    if first_run:
        dlg = SettingsWindow(None, cfg, on_saved=lambda new_cfg: (tray._on_config_saved(new_cfg)))
        dlg.ShowModal()
        dlg.Destroy()

    app.MainLoop()

    watcher.stop()


if __name__ == "__main__":
    main()
