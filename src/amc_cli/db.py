from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from .config import default_db_path


class Database:
    def __init__(self, path: str | Path | None = None):
        self.path = Path(path) if path else default_db_path()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.path)
        self.conn.row_factory = sqlite3.Row

    def init_db(self, schema_path: str | Path) -> None:
        schema = Path(schema_path).read_text(encoding="utf-8")
        self.conn.executescript(schema)
        self.conn.execute(
            "INSERT OR REPLACE INTO meta(key, value) VALUES (?, ?)", ("schema_version", "0.1.0")
        )
        self.conn.commit()

    def fetch_all(self, query: str, params: tuple = ()) -> list[sqlite3.Row]:
        return self.conn.execute(query, params).fetchall()

    def execute(self, query: str, params: tuple = ()) -> sqlite3.Cursor:
        return self.conn.execute(query, params)

    def commit(self) -> None:
        self.conn.commit()

    def close(self) -> None:
        self.conn.close()


def open_db(path: str | Path | None = None) -> Database:
    return Database(path)


def normalize_options(value):
    if value is None:
        return {}
    if isinstance(value, dict):
        return value
    if isinstance(value, str):
        return json.loads(value)
    return dict(value)
