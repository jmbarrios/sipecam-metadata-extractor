import logging

def setup_logging(logs_filename):
    file_handler = logging.FileHandler(logs_filename, mode='a')
    file_handler.setLevel(logging.INFO)
    logger = logging.getLogger()
    logger.setLevel(file_handler.level)
    logger.addHandler(file_handler)
    return logger


