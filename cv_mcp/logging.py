"""Structured logging setup shared by the MCP and download listeners."""

import logging
import os

import structlog


def setup_logging(level: str) -> None:
    """Configure one structured logging pipeline for application and server logs."""
    normalized_level = level.strip().upper()
    if normalized_level not in logging.getLevelNamesMapping():
        raise ValueError(f"Unsupported log level: {level!r}")

    log_format = os.getenv("CV_MCP_LOG_FORMAT", "json").strip().lower()
    if log_format == "console":
        renderer: structlog.types.Processor = structlog.dev.ConsoleRenderer()
    elif log_format == "json":
        renderer = structlog.processors.JSONRenderer()
    else:
        raise ValueError(f"Unsupported CV_MCP_LOG_FORMAT: {log_format!r}")

    shared_processors: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]
    formatter = structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=shared_processors,
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            renderer,
        ],
    )
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    structlog.configure(
        processors=[
            *shared_processors,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    logging.basicConfig(
        handlers=[handler],
        level=normalized_level,
        force=True,
    )
    logging.captureWarnings(True)
