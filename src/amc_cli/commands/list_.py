from __future__ import annotations

import json
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from ..config import default_db_path
from ..db import Database

console = Console()


def list_app(
    contest: str = typer.Option(None, "--contest"),
    year: int = typer.Option(None, "--year"),
    tag: str = typer.Option(None, "--tag"),
    difficulty: int = typer.Option(None, "--difficulty"),
    limit: int = typer.Option(20, "--limit"),
    json_output: bool = typer.Option(False, "--json"),
    db: str = typer.Option(default_db_path(), "--db"),
):
    """List questions with optional filters."""
    database = Database(db)
    query = "SELECT q.id, q.contest, q.year, q.paper, q.problem_no, q.difficulty, q.answer, q.has_solution FROM questions q"
    clauses = []
    params = []
    if contest:
        clauses.append("q.contest = ?")
        params.append(contest)
    if year is not None:
        clauses.append("q.year = ?")
        params.append(year)
    if difficulty is not None:
        clauses.append("q.difficulty = ?")
        params.append(difficulty)
    if clauses:
        query += " WHERE " + " AND ".join(clauses)
    query += " ORDER BY q.id DESC LIMIT ?"
    params.append(limit)
    rows = database.fetch_all(query, tuple(params))
    database.close()

    if json_output:
        typer.echo(json.dumps([dict(row) for row in rows], indent=2))
        return

    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("id")
    table.add_column("contest")
    table.add_column("year")
    table.add_column("paper")
    table.add_column("problem")
    table.add_column("difficulty")
    table.add_column("answer")
    for row in rows:
        table.add_row(str(row["id"]), row["contest"] or "", str(row["year"] or ""), row["paper"] or "", str(row["problem_no"] or ""), str(row["difficulty"] or ""), "yes" if row["answer"] else "no")
    console.print(table)
