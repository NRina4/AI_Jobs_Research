import logging
from importlib.metadata import PackageNotFoundError, version

import typer
from pydantic import ValidationError

from research_graph.config import get_settings
from research_graph.logging_setup import setup_logging

app = typer.Typer(help="Research Graph — инструменты исследовательского проекта.")
logger = logging.getLogger(__name__)


@app.command("version")
def version_cmd() -> None:
    """Показать версию приложения."""
    try:
        app_version = version("research-graph")
    except PackageNotFoundError:
        app_version = "unknown"

    typer.echo(f"Research Graph version: {app_version}")


@app.command("check-config")
def check_config() -> None:
    """Проверить настройки приложения без вывода секретов."""
    setup_logging()

    try:
        settings = get_settings()
    except ValidationError:
        logger.exception("Configuration validation failed")
        typer.echo("Configuration is invalid.", err=True)
        raise typer.Exit(code=1) from None

    typer.echo("Configuration is valid.")
    typer.echo(f"Data directory: {settings.data_dir}")
    typer.echo(f"Log level: {settings.log_level}")
    typer.echo(f"Request timeout: {settings.request_timeout}")
    typer.echo(f"Max concurrency: {settings.max_concurrency}")
    typer.echo(f"GitHub token configured: {'yes' if settings.github_token else 'no'}")


if __name__ == "__main__":
    app()
