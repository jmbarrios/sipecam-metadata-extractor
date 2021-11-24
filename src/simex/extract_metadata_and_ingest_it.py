import glob
import os
import re
import argparse
from argparse import RawTextHelpFormatter

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
    dirname_file = os.path.join(os.path.dirname(input_file),
                                "temp_logs_simex_extract_metadata_and_ingest")
    if not os.path.exists(dirname_file):
        os.makedirs(dirname_file)
    wav_extensions = "WAV|wav"
    jpg_extensions = "JPG|jpg"
    avi_extensions = "AVI|avi"

    if re.search(wav_extensions, input_file):
        print("WAV")
    if re.search(avi_extensions, input_file):
        print("AVI")
    if re.search(jpg_extensions, input_file):
        print("JPG")

