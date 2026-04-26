from __future__ import annotations

import wx

import tracker


class LogWindow(wx.Frame):
    def __init__(self, parent: wx.Window | None) -> None:
        super().__init__(
            parent,
            title="Penport — Job Log",
            size=wx.Size(900, 550),
            style=wx.DEFAULT_FRAME_STYLE,
        )
        self._build_ui()
        self._load_jobs()
        self.Centre()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        # Top: list control
        self._list = wx.ListCtrl(panel, style=wx.LC_REPORT | wx.BORDER_SUNKEN)
        self._list.InsertColumn(0, "Date / Time", width=160)
        self._list.InsertColumn(1, "File", width=220)
        self._list.InsertColumn(2, "Status", width=70)
        self._list.InsertColumn(3, "Output", width=280)
        self._list.Bind(wx.EVT_LIST_ITEM_SELECTED, self._on_select)

        # Bottom: detail panel
        self._detail = wx.TextCtrl(
            panel,
            style=wx.TE_MULTILINE | wx.TE_READONLY | wx.BORDER_SUNKEN,
            size=wx.Size(-1, 160),
        )

        # Toolbar
        btn_refresh = wx.Button(panel, label="Refresh")
        btn_refresh.Bind(wx.EVT_BUTTON, lambda _: self._load_jobs())

        toolbar = wx.BoxSizer(wx.HORIZONTAL)
        toolbar.Add(btn_refresh, 0, wx.ALL, 4)

        vbox.Add(toolbar, 0, wx.EXPAND)
        vbox.Add(self._list, 1, wx.EXPAND | wx.ALL, 4)
        vbox.Add(wx.StaticText(panel, label="Raw / Corrected text:"), 0, wx.LEFT | wx.TOP, 6)
        vbox.Add(self._detail, 0, wx.EXPAND | wx.ALL, 4)

        panel.SetSizer(vbox)

        self._jobs: list[dict] = []

    # ------------------------------------------------------------------
    # Data
    # ------------------------------------------------------------------

    def _load_jobs(self) -> None:
        self._jobs = tracker.get_recent_jobs(50)
        self._list.DeleteAllItems()
        for job in self._jobs:
            idx = self._list.InsertItem(self._list.GetItemCount(), job["processed_at"][:19])
            self._list.SetItem(idx, 1, job["filename"])
            self._list.SetItem(idx, 2, job["status"])
            self._list.SetItem(idx, 3, job.get("output_path") or "")
        self._detail.SetValue("")

    def _on_select(self, event: wx.ListEvent) -> None:
        idx = event.GetIndex()
        if idx < 0 or idx >= len(self._jobs):
            return
        job = self._jobs[idx]
        parts = []
        if job.get("raw_text"):
            parts.append("=== RAW ===\n" + job["raw_text"])
        if job.get("corrected_text"):
            parts.append("=== CORRECTED ===\n" + job["corrected_text"])
        if job.get("error_message"):
            parts.append("=== ERROR ===\n" + job["error_message"])
        self._detail.SetValue("\n\n".join(parts) if parts else "(no text recorded)")
