from __future__ import annotations

import tomllib
from pathlib import Path

APP_DIR = Path.home() / ".amc-cli"
CONFIG_PATH = APP_DIR / "config.toml"


def ensure_app_dir() -> Path:
    APP_DIR.mkdir(parents=True, exist_ok=True)
    return APP_DIR


def default_db_path() -> Path:
    ensure_app_dir()
    return APP_DIR / "amc.db"


def load_config() -> dict:
    if not CONFIG_PATH.exists():
        return {"target": "AMC12", "default_count": 10, "show_answer": False, "plain": False}
    with CONFIG_PATH.open("rb") as fh:
        data = tomllib.load(fh)
    if not isinstance(data, dict):
        return {"target": "AMC12", "default_count": 10, "show_answer": False, "plain": False}
    return {
        "target": data.get("target", "AMC12"),
        "default_count": int(data.get("default_count", 10)),
        "show_answer": bool(data.get("show_answer", False)),
        "plain": bool(data.get("plain", False)),
    }


def save_config(config: dict) -> None:
    ensure_app_dir()
    with CONFIG_PATH.open("w", encoding="utf-8") as fh:
        fh.write("[amc]\n")
        for key in ("target", "default_count", "show_answer", "plain"):
            value = config.get(key)
            if isinstance(value, bool):
                fh.write(f"{key} = {str(value).lower()}\n")
            else:
                fh.write(f"{key} = {value}\n")
