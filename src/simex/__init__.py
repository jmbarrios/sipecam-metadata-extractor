import logging
import os
import pathlib

SUFFIXES_SIPECAM_AUDIO  = [".WAV",
                           ".wav"]
SUFFIXES_SIPECAM_IMAGES = [".JPG",
                           ".jpg"]
SUFFIXES_SIPECAM_VIDEO  = [".AVI",
                           ".avi"]
SUFFIXES_SIPECAM = SUFFIXES_SIPECAM_AUDIO + SUFFIXES_SIPECAM_IMAGES + \
SUFFIXES_SIPECAM_VIDEO

def setup_logging(logs_filename):
    """
    Function that will open file to hold log of file processed.
    Args:
        logs_filename (str): empty file name, will hold logs.
    Returns:
        logger: instance of logging, commonly named RootLogger.
    """
    logFormatter = logging.Formatter("%(asctime)s [%(levelname)s]  %(message)s")
    file_handler = logging.FileHandler(logs_filename, mode='a')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logFormatter)
    logger = logging.getLogger()
    logger.setLevel(file_handler.level)
    logger.addHandler(file_handler)
    return logger

def get_logger_for_writing_logs_to_file(input_file_or_dir, filename_for_logs):
    """
    Helper function to setup logging to level specified
    in setup_logging function.
    Args:
        input_file_or_dir (str): file or directory that will be processed (includes path of file).
        It's used for creating file with logs.
        filename_for_logs (str): name of file that will hold logs files.
    Returns:
        getLogger instance from logging module.
    """
    input_file_or_dir_path_lib = pathlib.Path(input_file_or_dir)
    if input_file_or_dir_path_lib.suffix: #is file
        dirname_file = os.path.join(os.path.dirname(input_file_or_dir),
                                    filename_for_logs)
        os.makedirs(dirname_file, exist_ok=True)
        logs_filename = os.path.join(dirname_file,
                                     input_file_or_dir_path_lib.stem + \
                                     input_file_or_dir_path_lib.suffix + \
                                     ".logs")
    else: #is directory
        dirname_file = os.path.join(input_file_or_dir,
                                    filename_for_logs)
        logs_filename = dirname_file + ".logs"
    pathlib.Path(logs_filename).unlink(missing_ok=True) #remove in case it exists
    return setup_logging(logs_filename)


