import logging


def get_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    console = logging.StreamHandler()
    console.setFormatter(
        logging.Formatter(
            fmt="%(asctime)s %(levelname)s %(name)s:%(filename)s:%(lineno)s] "
            "%(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )
    logger = logging.getLogger(name)
    logger.addHandler(console)
    logger.setLevel(level)
    return logger
