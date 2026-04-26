from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

from platformdirs import user_data_dir

APP_NAME = "Penport"

_CONFIG_PATH: Path | None = None


def _config_path() -> Path:
    global _CONFIG_PATH
    if _CONFIG_PATH is None:
        data_dir = Path(user_data_dir(APP_NAME, appauthor=False))
        data_dir.mkdir(parents=True, exist_ok=True)
        _CONFIG_PATH = data_dir / "config.json"
    return _CONFIG_PATH


def _defaults() -> dict:
    home = Path.home()
    return {
        "folders": {
            "inbox": str(home / "Pictures" / "Penport" / "inbox"),
            "output": str(home / "Documents" / "Penport" / "output"),
        },
        "llm": {
            "vision_provider": "gemini",
            "vision_model": "gemini-2.5-flash",
            "vision_api_key": "",
            "correction_provider": "gemini",
            "correction_model": "gemini-2.5-flash",
            "correction_api_key": "",
        },
        "languages": {
            "primary": "English",
            "additional": [],
        },
        "output": {
            "format": "txt",
        },
        "pipeline": {
            "correction_enabled": True,
            "review_before_save": False,
            "poll_interval_seconds": 300,
        },
    }


def config_exists() -> bool:
    return _config_path().exists()


def load_config() -> dict:
    path = _config_path()
    if not path.exists():
        cfg = _defaults()
        save_config(cfg)
        return cfg
    with open(path, encoding="utf-8") as f:
        stored = json.load(f)
    # Merge with defaults so new keys are always present
    cfg = _defaults()
    _deep_merge(cfg, stored)
    return cfg


def save_config(cfg: dict) -> None:
    path = _config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2)
        os.replace(tmp, path)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def _deep_merge(base: dict, override: dict) -> None:
    for key, value in override.items():
        if key in base and isinstance(base[key], dict) and isinstance(value, dict):
            _deep_merge(base[key], value)
        else:
            base[key] = value


def languages_string(cfg: dict) -> str:
    langs = [cfg["languages"]["primary"]] + cfg["languages"].get("additional", [])
    return ", ".join(l for l in langs if l)
