from __future__ import annotations

from typing import Callable

import wx

from config import save_config
from providers import PROVIDER_NAMES


class SettingsWindow(wx.Dialog):
    def __init__(
        self,
        parent: wx.Window | None,
        cfg: dict,
        on_saved: Callable[[dict], None] | None = None,
    ) -> None:
        super().__init__(
            parent,
            title="Penport Settings",
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER,
        )
        self._cfg = cfg
        self._on_saved = on_saved
        self._build_ui()
        self._populate()
        self.Fit()
        self.SetMinSize(wx.Size(520, -1))
        self.Centre()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        root = wx.BoxSizer(wx.VERTICAL)
        nb = wx.Notebook(self)

        nb.AddPage(self._make_folders_page(nb), "Folders")
        nb.AddPage(self._make_vision_page(nb), "Vision LLM")
        nb.AddPage(self._make_correction_page(nb), "Correction LLM")
        nb.AddPage(self._make_languages_page(nb), "Languages")
        nb.AddPage(self._make_pipeline_page(nb), "Pipeline")

        root.Add(nb, 1, wx.EXPAND | wx.ALL, 8)

        # Buttons
        btns = self.CreateStdDialogButtonSizer(wx.OK | wx.CANCEL)
        root.Add(btns, 0, wx.EXPAND | wx.ALL, 8)

        self.Bind(wx.EVT_BUTTON, self._on_ok, id=wx.ID_OK)

        self.SetSizer(root)

    def _make_folders_page(self, parent: wx.Window) -> wx.Panel:
        page = wx.Panel(parent)
        gs = wx.FlexGridSizer(2, 3, 6, 6)
        gs.AddGrowableCol(1)

        gs.Add(wx.StaticText(page, label="Inbox folder:"), 0, wx.ALIGN_CENTER_VERTICAL)
        self._inbox = wx.TextCtrl(page)
        gs.Add(self._inbox, 1, wx.EXPAND)
        btn_inbox = wx.Button(page, label="Browse…")
        btn_inbox.Bind(wx.EVT_BUTTON, lambda _: self._browse_dir(self._inbox))
        gs.Add(btn_inbox)

        gs.Add(wx.StaticText(page, label="Output folder:"), 0, wx.ALIGN_CENTER_VERTICAL)
        self._output_folder = wx.TextCtrl(page)
        gs.Add(self._output_folder, 1, wx.EXPAND)
        btn_out = wx.Button(page, label="Browse…")
        btn_out.Bind(wx.EVT_BUTTON, lambda _: self._browse_dir(self._output_folder))
        gs.Add(btn_out)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(gs, 1, wx.EXPAND | wx.ALL, 12)
        page.SetSizer(sizer)
        return page

    def _make_vision_page(self, parent: wx.Window) -> wx.Panel:
        page = wx.Panel(parent)
        gs = wx.FlexGridSizer(3, 2, 6, 6)
        gs.AddGrowableCol(1)

        gs.Add(wx.StaticText(page, label="Provider:"), 0, wx.ALIGN_CENTER_VERTICAL)
        self._vision_provider = wx.Choice(page, choices=PROVIDER_NAMES)
        gs.Add(self._vision_provider, 1, wx.EXPAND)

        gs.Add(wx.StaticText(page, label="Model:"), 0, wx.ALIGN_CENTER_VERTICAL)
        self._vision_model = wx.TextCtrl(page)
        gs.Add(self._vision_model, 1, wx.EXPAND)

        gs.Add(wx.StaticText(page, label="API Key:"), 0, wx.ALIGN_CENTER_VERTICAL)
        self._vision_key = wx.TextCtrl(page, style=wx.TE_PASSWORD)
        gs.Add(self._vision_key, 1, wx.EXPAND)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(gs, 1, wx.EXPAND | wx.ALL, 12)
        page.SetSizer(sizer)
        return page

    def _make_correction_page(self, parent: wx.Window) -> wx.Panel:
        page = wx.Panel(parent)
        gs = wx.FlexGridSizer(3, 2, 6, 6)
        gs.AddGrowableCol(1)

        gs.Add(wx.StaticText(page, label="Provider:"), 0, wx.ALIGN_CENTER_VERTICAL)
        self._corr_provider = wx.Choice(page, choices=PROVIDER_NAMES)
        gs.Add(self._corr_provider, 1, wx.EXPAND)

        gs.Add(wx.StaticText(page, label="Model:"), 0, wx.ALIGN_CENTER_VERTICAL)
        self._corr_model = wx.TextCtrl(page)
        gs.Add(self._corr_model, 1, wx.EXPAND)

        gs.Add(wx.StaticText(page, label="API Key:"), 0, wx.ALIGN_CENTER_VERTICAL)
        self._corr_key = wx.TextCtrl(page, style=wx.TE_PASSWORD)
        gs.Add(self._corr_key, 1, wx.EXPAND)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(gs, 1, wx.EXPAND | wx.ALL, 12)
        page.SetSizer(sizer)
        return page

    def _make_languages_page(self, parent: wx.Window) -> wx.Panel:
        page = wx.Panel(parent)
        gs = wx.FlexGridSizer(2, 2, 6, 6)
        gs.AddGrowableCol(1)

        gs.Add(wx.StaticText(page, label="Primary language:"), 0, wx.ALIGN_CENTER_VERTICAL)
        self._lang_primary = wx.TextCtrl(page)
        gs.Add(self._lang_primary, 1, wx.EXPAND)

        gs.Add(
            wx.StaticText(page, label="Additional (comma-separated):"), 0, wx.ALIGN_CENTER_VERTICAL
        )
        self._lang_additional = wx.TextCtrl(page)
        gs.Add(self._lang_additional, 1, wx.EXPAND)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(gs, 1, wx.EXPAND | wx.ALL, 12)
        page.SetSizer(sizer)
        return page

    def _make_pipeline_page(self, parent: wx.Window) -> wx.Panel:
        page = wx.Panel(parent)
        vbox = wx.BoxSizer(wx.VERTICAL)

        self._correction_enabled = wx.CheckBox(page, label="Enable correction step")
        vbox.Add(self._correction_enabled, 0, wx.ALL, 8)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(
            wx.StaticText(page, label="Poll interval (seconds):"),
            0,
            wx.ALIGN_CENTER_VERTICAL | wx.RIGHT,
            8,
        )
        self._poll_interval = wx.SpinCtrl(page, min=10, max=3600, initial=300)
        hbox.Add(self._poll_interval, 0)
        vbox.Add(hbox, 0, wx.ALL, 8)

        page.SetSizer(vbox)
        return page

    # ------------------------------------------------------------------
    # Populate from config
    # ------------------------------------------------------------------

    def _populate(self) -> None:
        folders = self._cfg["folders"]
        self._inbox.SetValue(folders.get("inbox", ""))
        self._output_folder.SetValue(folders.get("output", ""))

        llm = self._cfg["llm"]
        self._vision_provider.SetStringSelection(llm.get("vision_provider", "gemini"))
        self._vision_model.SetValue(llm.get("vision_model", ""))
        self._vision_key.SetValue(llm.get("vision_api_key", ""))

        self._corr_provider.SetStringSelection(llm.get("correction_provider", "gemini"))
        self._corr_model.SetValue(llm.get("correction_model", ""))
        self._corr_key.SetValue(llm.get("correction_api_key", ""))

        langs = self._cfg["languages"]
        self._lang_primary.SetValue(langs.get("primary", ""))
        self._lang_additional.SetValue(", ".join(langs.get("additional", [])))

        pipeline = self._cfg["pipeline"]
        self._correction_enabled.SetValue(pipeline.get("correction_enabled", True))
        self._poll_interval.SetValue(pipeline.get("poll_interval_seconds", 300))

    # ------------------------------------------------------------------
    # Save
    # ------------------------------------------------------------------

    def _on_ok(self, event: wx.CommandEvent) -> None:
        self._cfg["folders"]["inbox"] = self._inbox.GetValue().strip()
        self._cfg["folders"]["output"] = self._output_folder.GetValue().strip()

        llm = self._cfg["llm"]
        llm["vision_provider"] = self._vision_provider.GetStringSelection()
        llm["vision_model"] = self._vision_model.GetValue().strip()
        llm["vision_api_key"] = self._vision_key.GetValue().strip()
        llm["correction_provider"] = self._corr_provider.GetStringSelection()
        llm["correction_model"] = self._corr_model.GetValue().strip()
        llm["correction_api_key"] = self._corr_key.GetValue().strip()

        self._cfg["languages"]["primary"] = self._lang_primary.GetValue().strip()
        additional_raw = self._lang_additional.GetValue()
        self._cfg["languages"]["additional"] = [
            s.strip() for s in additional_raw.split(",") if s.strip()
        ]

        self._cfg["pipeline"]["correction_enabled"] = self._correction_enabled.GetValue()
        self._cfg["pipeline"]["poll_interval_seconds"] = self._poll_interval.GetValue()

        save_config(self._cfg)

        if self._on_saved:
            self._on_saved(self._cfg)

        self.EndModal(wx.ID_OK)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _browse_dir(self, target: wx.TextCtrl) -> None:
        dlg = wx.DirDialog(self, "Choose a folder", style=wx.DD_DEFAULT_STYLE)
        if dlg.ShowModal() == wx.ID_OK:
            target.SetValue(dlg.GetPath())
        dlg.Destroy()
