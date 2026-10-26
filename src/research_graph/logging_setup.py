import logging

from research_graph.config import get_settings


def setup_logging() -> None:
    """Настроить журналирование приложения."""
    settings = get_settings()

    logging.basicConfig(
        level=settings.log_level.upper(),
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
