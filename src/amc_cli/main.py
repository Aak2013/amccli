from __future__ import annotations

import typer
from rich.console import Console

from .commands.config import config_app
from .commands.init import init_app
from .commands.import_ import import_app
from .commands.list_ import list_app
from .commands.show import show_app
from .commands.practice import practice_app
from .commands.review import review_app
from .commands.stats import stats_app
from .commands.recommend import recommend_app
from .config import default_db_path, load_config

app = typer.Typer(add_completion=False, help="AMC practice CLI")
console = Console()


@app.callback()
def main(
    ctx: typer.Context,
    db: str = typer.Option(default_db_path(), "--db", help="Path to the SQLite database."),
    plain: bool = typer.Option(False, "--plain", help="Simplify LaTeX output for terminal display."),
    no_color: bool = typer.Option(False, "--no-color", help="Disable ANSI colors."),
    version: bool = typer.Option(False, "--version", help="Show version and exit.", is_eager=True),
):
    ctx.ensure_object(dict)
    ctx.obj["db"] = db
    ctx.obj["plain"] = plain
    ctx.obj["no_color"] = no_color
    ctx.obj["config"] = load_config()
    if no_color:
        console.no_color = True
    if version:
        typer.echo("amc-cli 0.1.0")
        raise typer.Exit()


app.add_typer(config_app, name="config")
app.command("init")(init_app)
app.command("import")(import_app)
app.command("list")(list_app)
app.command("show")(show_app)
app.command("practice")(practice_app)
app.command("review")(review_app)
app.command("stats")(stats_app)
app.command("recommend")(recommend_app)


if __name__ == "__main__":
    app()
