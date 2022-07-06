import os
import re
import argparse
import pathlib
import json
import datetime

import exiftool
from simex import get_logger_for_writing_logs_to_file
from simex.utils.directories_and_files import multiple_file_types

def arguments_parse():
    help = """
Traverse files in a directory to extend metadata of audio files

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
    pattern = ["[0-9][0-9]-[0-9][0-9]-[0-9][0-9][0-9][0-9].json"]#for json filename which includes date in "%d-%m-%Y" format
    iterator = multiple_file_types(input_directory, pattern)
    list_json_files = []
    for json_file in iterator:
        json_file_pathlib = pathlib.Path(json_file)
        json_filename = str(json_file_pathlib.name)
        list_json_files.append(json_filename)

    date_format = "%d-%m-%Y"
    list_datetimes_of_json_files = [datetime.datetime.strptime(re.findall("[0-9]{2}-[0-9]{2}-[0-9]{4}", s)[0],
                                                               date_format) for s in list_json_files]
    list_datetimes_of_json_files.sort()
    list_dates_json_files_sorted = [d.strftime(date_format) for d in list_datetimes_of_json_files]
    last_date = list_dates_json_files_sorted[len(list_dates_json_files_sorted)-1]
    file_with_audio_metadata_source =os.path.join(input_directory,
                                                  input_directory_name + \
                                                  "_simex_metadata_files_and_device_" + \
                                                  last_date + \
                                                  ".json")
    logger.info("Json file that will be the source: %s" % file_with_audio_metadata_source)

    with open(file_with_audio_metadata_source, 'r') as f:
        dict_source = json.load(f)
    
    f1 = "/LUSTRE/sacmod/SIPECAM/data/32/4_32_0_1280/2453AC025DAEB669/2021-08-23/audios/Ultrasonico/67acc1799111d5ab3fa7bad695676f1a.WAV"
    dict_f1 = {"Battery": "4.6V",
               "Datetime": "04:40:00 02/09/2021 (UTC-0600)",
               "Gain": "medium",
               "Timezone": "UTC",
               "BitRate": "6.1 Mbit/sec",
               "SerialNumber": "2453AC025DAEB669",
               "FileSize": "7.0 MiB",
               "Encoding": "Microsoft PCM",
               "NumChannels": 1,
               "SampleRate": 384000,
               "AvgBytesPerSec": 768000,
               "BitsPerSample": 16,
               "Comment": "Recorded at 04:40:00 02/09/2021 (UTC-6) by AudioMoth 2453AC025DAEB669 at medium gain setting while battery state was 4.6V and temperature was 20.1C.",
               "Duration": "9.56 s",
               "Latitude": 18.49711,
               "Longitude": -99.14328,
               "CentroidCumulusLatitude": 18.42113,
               "CentroidCumulusLongitude": -99.09369
              }
    
    dict_source["MetadataFiles"][f1]  = dict_f1
    
    file_with_audio_metadata_dst = os.path.join(input_directory,
                                                input_directory_name) + \
                                                "_simex_metadata_files_and_device_" + \
                                                datetime.date.today().strftime(date_format) + \
                                                ".json"
    pathlib.Path(file_with_audio_metadata_dst).unlink(missing_ok=True) #remove in case it exists
    with open(file_with_audio_metadata_dst, 'w') as dst:
        json.dump(dict_source, dst)
