from __future__ import annotations

import typer

from ..config import default_db_path
from ..db import Database


def review_app(
    due: bool = typer.Option(False, "--due"),
    count: int = typer.Option(10, "--count"),
    db: str = typer.Option(default_db_path(), "--db"),
):
    """List incorrect questions due for review."""
    database = Database(db)
    rows = database.fetch_all(
        "SELECT q.id, q.contest, q.year, q.problem_no, a.created_at FROM attempts a JOIN questions q ON q.id = a.question_id WHERE a.is_correct = 0 ORDER BY a.created_at DESC LIMIT ?",
        (count,),
    )
    database.close()
    if not rows:
        typer.echo("No incorrect attempts found.")
        return
    for row in rows:
        typer.echo(f"#{row['id']} | {row['contest']} {row['year']} {row['problem_no']} | {row['created_at']}")
