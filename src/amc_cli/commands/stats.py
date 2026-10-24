from __future__ import annotations

import typer

from ..config import default_db_path
from ..db import Database


def stats_app(
    tag: str = typer.Option(None, "--tag"),
    db: str = typer.Option(default_db_path(), "--db"),
):
    """Display basic statistics and mastery summaries."""
    database = Database(db)
    if tag:
        row = database.fetch_all(
            "SELECT COUNT(*) AS n FROM questions q JOIN question_tags qt ON qt.question_id = q.id JOIN tags t ON t.id = qt.tag_id WHERE t.name = ?",
            (tag,),
        )
        typer.echo(f"Tag: {tag}")
        typer.echo(f"Question count: {row[0]['n']}")
        database.close()
        return

    rows = database.fetch_all(
        "SELECT t.name, COUNT(qt.question_id) AS count FROM tags t LEFT JOIN question_tags qt ON qt.tag_id = t.id GROUP BY t.name ORDER BY count DESC"
    )
    database.close()
    if not rows:
        typer.echo("No tags yet. Import some questions first.")
        return
    for row in rows:
        typer.echo(f"{row['name']}: {row['count']} questions")
