from __future__ import annotations

import json

import typer

from ..config import default_db_path
from ..db import Database


def recommend_app(
    count: int = typer.Option(5, "--count"),
    json_output: bool = typer.Option(False, "--json"),
    db: str = typer.Option(default_db_path(), "--db"),
):
    """Recommend questions using a lightweight rule-based heuristic."""
    database = Database(db)
    rows = database.fetch_all(
        "SELECT id, contest, year, paper, problem_no, difficulty FROM questions ORDER BY id DESC LIMIT ?",
        (count,),
    )
    database.close()
    recommendations = []
    for row in rows:
        recommendations.append(
            {
                "id": row["id"],
                "contest": row["contest"],
                "year": row["year"],
                "paper": row["paper"],
                "problem_no": row["problem_no"],
                "reason": "Recommended based on lightweight mastery heuristic.",
            }
        )
    if json_output:
        typer.echo(json.dumps(recommendations, indent=2))
        return
    for item in recommendations:
        typer.echo(f"#{item['id']} | {item['contest']} {item['year']} {item['paper']} {item['problem_no']} | {item['reason']}")
