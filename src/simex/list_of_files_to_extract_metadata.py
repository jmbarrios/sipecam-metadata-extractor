import glob
import os
import re
import datetime
import argparse
from argparse import RawTextHelpFormatter

def arguments_parse():
    help = """
Given a directory with SiPeCaM files, produce list of files that whose metadata
will be extracted and list of directories where data will be copied
(traditional server).
--------------
Example usage:
--------------

list_of_files_to_extract_metadata --input_directory /input_dir
                                  --output_directory /output_dir

"""


    parser = argparse.ArgumentParser(description=help,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--input_directory",
                        required=True,
                        default=None,
                        help="Help of test argparse fun")
    parser.add_argument("--output_directory",
                        required=True,
                        default=None,
                        help="Help of test argparse fun")
    args = parser.parse_args()
    return args

def main():
    args = arguments_parse()
    input_directory = args.input_directory
    output_directory = args.output_directory
    sipecam_files_to_extract_metadata = os.path.join(os.path.expanduser("~"),
                                        "sipecam_files_to_extract_metadata_from_" + \
                                        datetime.date.today().strftime("%m-%d-%Y") + \
                                        ".txt")
    wav_extensions = "WAV|wav"
    jpg_extensions = "JPG|jpg"
    avi_extensions = "AVI|avi"
    reg_exp_extensions_for_glob = "*" + "[" + wav_extensions + \
                                  jpg_extensions + avi_extensions + "]"
    options = os.path.join(input_directory, "**", reg_exp_extensions_for_glob)
    with open(sipecam_files_to_extract_metadata,"w+") as file:
        for f in glob.iglob(options, recursive=True):
            file.write(f + "\n")

