import glob
import os
import re
import argparse
from argparse import RawTextHelpFormatter

from . import get_logger_for_writing_logs_to_file

def arguments_parse():
    help = """
Extract metadata of file, fill fields of File model in
Zendro and copy file to directory of server. Write logs for each
step.

--------------
Example usage:
--------------

extract_metadata_and_ingest_it --input_file filename.(WAV|JPG|AVI)

"""


    parser = argparse.ArgumentParser(description=help,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--input_file",
                        required=True,
                        default=None,
                        help="File that will be processed")
    args = parser.parse_args()
    return args

def main():
    args = arguments_parse()
    input_file = args.input_file
    logger = get_logger_for_writing_logs_to_file(input_file)
    logger.info("extract metadata and ingest it")
    wav_extensions = "WAV|wav"
    jpg_extensions = "JPG|jpg"
    avi_extensions = "AVI|avi"

    if re.search(wav_extensions, input_file):
        logger.info("WAV")
    if re.search(avi_extensions, input_file):
        logger.info("AVI")
    if re.search(jpg_extensions, input_file):
        logger.info("JPG")

