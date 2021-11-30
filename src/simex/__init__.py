import logging

def setup_logging(logs_filename):
    logFormatter = logging.Formatter("%(asctime)s [%(levelname)-5.5s]  %(message)s")
    file_handler = logging.FileHandler(logs_filename, mode='a')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logFormatter)
    logger = logging.getLogger()
    logger.setLevel(file_handler.level)
    logger.addHandler(file_handler)
    return logger


