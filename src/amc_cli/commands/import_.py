from __future__ import annotations

import json
from pathlib import Path

import typer

from ..config import default_db_path
from ..db import Database


def import_app(
    path: str = typer.Argument(..., help="Path to a JSONL file of questions."),
    dry_run: bool = typer.Option(False, "--dry-run"),
    dedupe: bool = typer.Option(False, "--dedupe"),
    limit: int = typer.Option(None, "--limit"),
    db: str = typer.Option(default_db_path(), "--db"),
):
    """Import AMC-style questions from JSONL."""
    source = Path(path)
    if not source.exists():
        typer.echo(f"Input file not found: {source}")
        raise typer.Exit(code=1)

    database = Database(db)
    counts = {"total": 0, "inserted": 0, "failed": 0}
    seen = set()
    failed_path = source.with_name(f"{source.stem}.import_failed.jsonl")
    with source.open("r", encoding="utf-8") as fh:
        for line_no, line in enumerate(fh, 1):
            if not line.strip():
                continue
            counts["total"] += 1
            if limit is not None and counts["total"] > limit:
                break
            try:
                payload = json.loads(line)
                identity = (
                    payload.get("contest"),
                    payload.get("year"),
                    payload.get("paper"),
                    payload.get("problem_no"),
                )
                if dedupe and identity in seen:
                    continue
                seen.add(identity)
                options_json = json.dumps(payload.get("options", {}))
                database.execute(
                    "INSERT INTO questions(contest, year, paper, problem_no, stem, options_json, answer, solution, difficulty, source, has_solution) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (
                        payload.get("contest"),
                        payload.get("year"),
                        payload.get("paper"),
                        payload.get("problem_no"),
                        payload.get("stem"),
                        options_json,
                        payload.get("answer"),
                        payload.get("solution"),
                        payload.get("difficulty"),
                        source.name,
                        int(bool(payload.get("solution"))),
                    ),
                )
                counts["inserted"] += 1
            except Exception as exc:  # pragma: no cover - import hygiene
                counts["failed"] += 1
                with failed_path.open("a", encoding="utf-8") as out:
                    out.write(json.dumps({"line": line_no, "payload": line.strip(), "error": str(exc)}) + "\n")

    if not dry_run:
        database.commit()
    database.close()
    typer.echo(
        f"Imported {counts['inserted']} questions; {counts['failed']} failed; {counts['total']} indexed total."
    )
    if failed_path.exists() and counts['failed']:
        typer.echo(f"Failed rows logged to {failed_path}")
