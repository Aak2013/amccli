from __future__ import annotations

from pathlib import Path

import typer

from ..config import default_db_path
from ..db import Database


def init_app(db: str = typer.Option(default_db_path(), "--db", help="Path to the SQLite database.")):
    """Initialize the local AMC database."""
    db_path = Path(db)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    database = Database(db_path)
    database.init_db(Path(__file__).resolve().parents[1] / "schema.sql")
    database.close()
    typer.echo(f"Initialized SQLite database at {db_path}")
