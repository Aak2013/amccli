from __future__ import annotations

from pathlib import Path

import typer

from ..config import default_db_path
from ..db import Database, normalize_options
from ..render import render_question


def practice_app(
    count: int = typer.Option(10, "--count"),
    tag: str = typer.Option(None, "--tag"),
    contest: str = typer.Option(None, "--contest"),
    difficulty: str = typer.Option(None, "--difficulty"),
    db: str = typer.Option(default_db_path(), "--db"),
):
    """Practice a batch of questions interactively."""
    database = Database(db)
    query = "SELECT * FROM questions"
    clauses = []
    params = []
    if contest:
        clauses.append("contest = ?")
        params.append(contest)
    if tag:
        clauses.append("id IN (SELECT question_id FROM question_tags qt JOIN tags t ON t.id = qt.tag_id WHERE t.name = ?)")
        params.append(tag)
    if difficulty:
        clauses.append("difficulty = ?")
        params.append(int(str(difficulty).split("-")[0]))
    if clauses:
        query += " WHERE " + " AND ".join(clauses)
    rows = database.fetch_all(query, tuple(params))
    sample = rows[:count]
    if not sample:
        typer.echo("No questions available. Import data first with `amc import`.")
        raise typer.Exit(code=1)
    for idx, row in enumerate(sample, 1):
        question = dict(row)
        question["options"] = normalize_options(question["options_json"])
        typer.echo(f"\n[{idx}/{len(sample)}] {question.get('contest', '')} {question.get('year', '')} {question.get('problem_no', '')}")
        typer.echo(render_question(question, plain=False, with_answer=False, with_solution=False))
        response = typer.prompt("Your answer (A-E, s=skip, q=quit)", default="")
        if response.lower() in {"q", "quit"}:
            typer.echo("Practice interrupted; progress saved to attempts.")
            break
        database.execute(
            "INSERT INTO attempts(question_id, user_choice, is_correct, elapsed_sec, mode) VALUES (?, ?, ?, ?, ?)",
            (question["id"], response.strip().upper(), 1 if response.strip().upper() == (question.get("answer") or "").upper() else 0, 0, "practice"),
        )
        database.commit()
    database.close()
    typer.echo(f"Completed practice round: {len(sample)} question(s).")
