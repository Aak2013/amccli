from __future__ import annotations

import json

import typer

from ..config import default_db_path
from ..db import Database, normalize_options
from ..render import render_question


def show_app(
    question_id: int = typer.Argument(...),
    with_answer: bool = typer.Option(False, "--with-answer"),
    with_solution: bool = typer.Option(False, "--with-solution"),
    plain: bool = typer.Option(False, "--plain"),
    db: str = typer.Option(default_db_path(), "--db"),
):
    """Display a single question."""
    database = Database(db)
    row = database.fetch_all(
        "SELECT * FROM questions WHERE id = ?",
        (question_id,),
    )
    database.close()
    if not row:
        typer.echo(f"Question {question_id} not found. Try `amc list`.")
        raise typer.Exit(code=1)
    question = dict(row[0])
    question["options"] = normalize_options(question["options_json"])
    typer.echo(render_question(question, plain=plain, with_answer=with_answer, with_solution=with_solution))
