import json
import logging
import logging.handlers
from datetime import datetime, timezone
from pathlib import Path

from models.metrics import HealthMetrics


class JsonFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data)


def setup_logger(name: str, log_dir: str = "logs") -> logging.Logger:
    """
    Setup logger with file rotation and JSON formatting.

    Args:
        name: Logger name
        log_dir: Directory for log files

    Returns:
        Configured logger instance
    """
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)

    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    # File handler with rotation (daily)
    log_file = log_path / "inspector.log"
    file_handler = logging.handlers.TimedRotatingFileHandler(
        filename=log_file,
        when="midnight",  # Rotate at midnight
        interval=1,       # Every day
        backupCount=7,    # Keep 7 days of logs
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(JsonFormatter())
    logger.addHandler(file_handler)

    # Console handler (without JSON, readable format)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_format = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)

    return logger


def log_metrics(logger: logging.Logger, metrics: HealthMetrics) -> None:
    """
    Log metrics as structured JSON.

    Args:
        logger: Logger instance
        metrics: HealthMetrics object
    """
    metrics_data = {
        "event": "metrics_collected",
        "node": metrics.node_name,
        "timestamp": metrics.timestamp.isoformat(),
        "metrics": {
            "block_height": metrics.block_height,
            "current_block_height": metrics.current_block_height,
            "peers_count": metrics.peers_count,
            "finality_lag": metrics.finality_lag,
            "time_since_last_block_seconds": metrics.time_since_last_block,
            "rpc_response_time_ms": metrics.rpc_response_time,
        },
        "status": metrics.status,
    }

    # Log as JSON
    logger.info(json.dumps(metrics_data))
