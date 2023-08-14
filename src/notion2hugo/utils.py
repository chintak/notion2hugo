import logging


def get_logger(name: str) -> logging.Logger:
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(
        logging.Formatter(
            fmt="%(asctime)s %(levelname)s %(name)s:%(filename)s:%(lineno)s] "
            "%(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )
    logger = logging.getLogger(name)
    logger.addHandler(console)
    return logger
