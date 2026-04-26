from __future__ import annotations

import os
import queue
import sys
import threading
from datetime import date
from pathlib import Path
from typing import Literal

import wx
import wx.adv

import tracker
from config import save_config
from log_window import LogWindow
from pipeline import run_pipeline
from settings_window import SettingsWindow
from watcher import Watcher

_ICON_DIR = Path(__file__).parent / "icons"

TrayState = Literal["idle", "processing", "error"]


class TrayIcon(wx.adv.TaskBarIcon):
    def __init__(self, cfg: dict, job_queue: queue.Queue) -> None:
        super().__init__()
        self._cfg = cfg
        self._job_queue = job_queue
        self._watcher: Watcher | None = None
        self._log_window: LogWindow | None = None
        self._settings_window: SettingsWindow | None = None
        self._state: TrayState = "idle"

        self._icons = self._load_icons()
        self._processing_frames: list[wx.Icon] = []
        self._frame_idx = 0
        self._anim_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self._on_anim_tick, self._anim_timer)

        self._set_icon("idle")
        self.Bind(wx.adv.EVT_TASKBAR_LEFT_DCLICK, self._on_left_dclick)

    # ------------------------------------------------------------------
    # Icon management
    # ------------------------------------------------------------------

    def _load_icons(self) -> dict[str, wx.Icon]:
        icons: dict[str, wx.Icon] = {}
        for name in ("idle", "processing", "error"):
            path = _ICON_DIR / f"{name}.png"
            if path.exists():
                ico = wx.Icon()
                ico.CopyFromBitmap(wx.Bitmap(str(path), wx.BITMAP_TYPE_PNG))
                icons[name] = ico
            else:
                # Fallback: coloured 16×16 bitmap
                icons[name] = self._make_fallback_icon(name)
        return icons

    def _make_fallback_icon(self, name: str) -> wx.Icon:
        colours = {"idle": (160, 160, 160), "processing": (50, 150, 250), "error": (220, 50, 50)}
        r, g, b = colours.get(name, (128, 128, 128))
        bmp = wx.Bitmap(16, 16)
        dc = wx.MemoryDC(bmp)
        dc.SetBackground(wx.Brush(wx.Colour(r, g, b)))
        dc.Clear()
        dc.SelectObject(wx.NullBitmap)
        ico = wx.Icon()
        ico.CopyFromBitmap(bmp)
        return ico

    def _set_icon(self, state: TrayState) -> None:
        self._state = state
        label = {"idle": "Penport — idle", "processing": "Penport — processing", "error": "Penport — error"}[state]
        if state == "processing":
            self._anim_timer.Start(500)
        else:
            self._anim_timer.Stop()
            self.SetIcon(self._icons[state], label)

    def _on_anim_tick(self, _event: wx.TimerEvent) -> None:
        self.SetIcon(self._icons["processing"], "Penport — processing")

    def set_state(self, state: TrayState) -> None:
        self._set_icon(state)

    # ------------------------------------------------------------------
    # Context menu
    # ------------------------------------------------------------------

    def CreatePopupMenu(self) -> wx.Menu:  # noqa: N802 (wx naming convention)
        menu = wx.Menu()

        item_sync = menu.Append(wx.ID_ANY, "Sync Now")
        self.Bind(wx.EVT_MENU, self._on_sync_now, item_sync)

        item_open = menu.Append(wx.ID_ANY, "Open Last Output")
        last = tracker.get_last_output_path()
        item_open.Enable(bool(last and Path(last).exists()))
        self.Bind(wx.EVT_MENU, self._on_open_last, item_open)

        menu.AppendSeparator()

        item_settings = menu.Append(wx.ID_ANY, "Settings")
        self.Bind(wx.EVT_MENU, self._on_settings, item_settings)

        item_log = menu.Append(wx.ID_ANY, "View Log")
        self.Bind(wx.EVT_MENU, self._on_view_log, item_log)

        menu.AppendSeparator()

        item_quit = menu.Append(wx.ID_ANY, "Quit")
        self.Bind(wx.EVT_MENU, self._on_quit, item_quit)

        return menu

    # ------------------------------------------------------------------
    # Menu handlers
    # ------------------------------------------------------------------

    def _on_left_dclick(self, _event: wx.adv.TaskBarIconEvent) -> None:
        self._show_log()

    def _on_sync_now(self, _event: wx.CommandEvent) -> None:
        if self._watcher:
            self._watcher.trigger_now()

    def _on_open_last(self, _event: wx.CommandEvent) -> None:
        last = tracker.get_last_output_path()
        if last and Path(last).exists():
            self._open_file(last)

    def _on_settings(self, _event: wx.CommandEvent) -> None:
        if self._settings_window and self._settings_window.IsShown():
            self._settings_window.Raise()
            return
        self._settings_window = SettingsWindow(None, self._cfg, on_saved=self._on_config_saved)
        self._settings_window.ShowModal()

    def _on_view_log(self, _event: wx.CommandEvent) -> None:
        self._show_log()

    def _on_quit(self, _event: wx.CommandEvent) -> None:
        if self._watcher:
            self._watcher.stop()
        self.RemoveIcon()
        wx.CallAfter(wx.GetApp().ExitMainLoop)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _show_log(self) -> None:
        if self._log_window and self._log_window.IsShown():
            self._log_window.Raise()
            return
        self._log_window = LogWindow(None)
        self._log_window.Show()

    def _on_config_saved(self, new_cfg: dict) -> None:
        self._cfg = new_cfg
        if self._watcher:
            self._watcher.reload_config(new_cfg)
            self._watcher.trigger_now()

    @staticmethod
    def _open_file(path: str) -> None:
        if sys.platform == "win32":
            os.startfile(path)  # type: ignore[attr-defined]
        elif sys.platform == "darwin":
            os.system(f'open "{path}"')
        else:
            os.system(f'xdg-open "{path}"')

    def attach_watcher(self, watcher: Watcher) -> None:
        self._watcher = watcher

    # ------------------------------------------------------------------
    # Notification helpers (called via wx.CallAfter)
    # ------------------------------------------------------------------

    def notify_success(self, filename: str, output_path: str) -> None:
        self.set_state("idle")
        msg = wx.adv.NotificationMessage(
            title="Penport",
            message=f"Transcribed: {filename}",
        )
        msg.Show(timeout=wx.adv.NotificationMessage.Timeout_Auto)

    def notify_error(self, filename: str, error: str) -> None:
        self.set_state("error")
        msg = wx.adv.NotificationMessage(
            title="Penport — Error",
            message=f"{filename}: {error}",
        )
        msg.Show(timeout=wx.adv.NotificationMessage.Timeout_Auto)


# ------------------------------------------------------------------
# Worker thread
# ------------------------------------------------------------------

class WorkerThread(threading.Thread):
    def __init__(self, cfg: dict, job_queue: queue.Queue, tray: TrayIcon) -> None:
        super().__init__(daemon=True, name="PenportWorker")
        self._cfg = cfg
        self._job_queue = job_queue
        self._tray = tray

    def run(self) -> None:
        while True:
            image_path: Path = self._job_queue.get()
            wx.CallAfter(self._tray.set_state, "processing")
            try:
                raw, corrected = run_pipeline(
                    image_path,
                    self._cfg,
                    progress_cb=None,
                )
                output_path = self._write_output(corrected or raw)
                tracker.record_success(
                    filename=image_path.name,
                    inbox_path=str(image_path),
                    output_path=output_path,
                    raw_text=raw,
                    corrected_text=corrected,
                )
                wx.CallAfter(self._tray.notify_success, image_path.name, output_path)
            except Exception as exc:
                tracker.record_error(
                    filename=image_path.name,
                    inbox_path=str(image_path),
                    error_message=str(exc),
                )
                wx.CallAfter(self._tray.notify_error, image_path.name, str(exc))
            finally:
                self._job_queue.task_done()

    def _write_output(self, text: str) -> str:
        output_dir = Path(self._cfg["folders"]["output"]).expanduser()
        output_dir.mkdir(parents=True, exist_ok=True)
        today = date.today().isoformat()
        out_file = output_dir / f"{today}.txt"
        if out_file.exists():
            with open(out_file, "a", encoding="utf-8") as f:
                f.write("\n---\n" + text)
        else:
            with open(out_file, "w", encoding="utf-8") as f:
                f.write(text)
        return str(out_file)

    def reload_config(self, cfg: dict) -> None:
        self._cfg = cfg
