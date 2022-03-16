import os
import argparse
import pathlib
import json
import datetime

from simex import get_logger_for_writing_logs_to_file
from simex.utils.directories_and_files import multiple_file_types

def arguments_parse():
    help = """
Traverse files in a directory to check if audio files are empty

--------------
Example usage:
--------------

extend_metadata_of_audio_files --input_directory_audio /dir/

"""


    parser = argparse.ArgumentParser(description=help,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--input_directory_audio",
                        required=True,
                        default=None,
                        help="Directory with WAV files")
    args = parser.parse_args()
    return args

def main():
    args = arguments_parse()
    input_directory = args.input_directory_audio
    filename_for_logs = "logs_simex_extend_metadata_of_audio_files"
    logger = get_logger_for_writing_logs_to_file(input_directory,
                                                 filename_for_logs)
    input_directory_name = pathlib.Path(input_directory).name
    file_with_audio_metadata_source = os.path.join(input_directory,
                                                   input_directory_name) + \
                                                   "_simex_metadata_files_and_device.json"
    with open(file_with_audio_metadata_source, 'r') as f:
        dict_source = json.load(f)
    lat  = dict_source["MetadataDevice"]["Latitude"]
    long = dict_source["MetadataDevice"]["Longitude"]
    for filename, metadata_file in dict_source["MetadataFiles"].items():
        dict_source["MetadataFiles"][filename]["Latitude"]  = lat
        dict_source["MetadataFiles"][filename]["Longitude"] = long
    file_with_audio_metadata_dst = os.path.join(input_directory,
                                                input_directory_name) + \
                                                "_simex_metadata_files_and_device_" + \
                                                datetime.date.today().strftime("%d-%m-%Y") + \
                                                ".json"
    with open(file_with_audio_metadata_dst, 'w') as dst:
        json.dump(dict_source, dst)
