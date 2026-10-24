from __future__ import annotations

import typer

from ..config import load_config, save_config

config_app = typer.Typer(help="Manage local AMC CLI configuration.")


@config_app.command("show")
def show_config():
    """Display the current configuration."""
    typer.echo(load_config())


@config_app.command("set")
def set_config(
    key: str = typer.Argument(..., help="Config key to set."),
    value: str = typer.Argument(..., help="New value for the key."),
):
    """Set a configuration value."""
    config = load_config()
    if key == "default_count":
        config[key] = int(value)
    elif key in {"show_answer", "plain"}:
        config[key] = value.lower() in {"1", "true", "yes", "y"}
    else:
        config[key] = value
    save_config(config)
    typer.echo(f"Updated {key} = {config[key]}")


if __name__ == "__main__":
    config_app()
