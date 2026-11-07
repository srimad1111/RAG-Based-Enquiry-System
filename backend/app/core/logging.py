import logging
import sys


def setup_logging(debug: bool = True) -> logging.Logger:
    """Configure application-wide logging without spamming asyncio/anyio debug logs."""
    log_format = "%(asctime)s - [%(levelname)s] - [%(name)s] - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    # Root logger at INFO to prevent library noise
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        datefmt=date_format,
        handlers=[logging.StreamHandler(sys.stdout)]
    )

    # NexaDesk application logger
    logger = logging.getLogger("nexadesk_backend")
    logger.setLevel(logging.DEBUG if debug else logging.INFO)

    # Silence verbose internal debug logs
    logging.getLogger("asyncio").setLevel(logging.WARNING)
    logging.getLogger("anyio").setLevel(logging.WARNING)

    return logger


logger = setup_logging()
