import glob
import os
import argparse
import json
import pathlib
from operator import itemgetter
import datetime

from simex import get_logger_for_writing_logs_to_file
from simex import SUFFIXES_SIPECAM_AUDIO, SUFFIXES_SIPECAM_IMAGES
from simex.utils.directories_and_files import multiple_file_types
from simex import read_metadata_image, read_metadata_audio

SUFFIXES_TARGET = SUFFIXES_SIPECAM_AUDIO + SUFFIXES_SIPECAM_IMAGES

def arguments_parse():
    help = """
Traverse files in a directory to extract serial number and coordinates of them.

--------------
Example usage:
--------------

extract_serial_numbers_datetime_and_coordinates_of_files --input_dir /dir/

"""


    parser = argparse.ArgumentParser(description=help,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--input_directory",
                        required=True,
                        default=None,
                        help="Directory with WAV, JPG and AVI files")
    parser.add_argument('--mixed',
                        action='store_true',
                        help='Directory contains mixture of files taken by different devices?')
    args = parser.parse_args()
    return args

def main():
    args = arguments_parse()
    input_directory = args.input_directory
    mixed = args.mixed
    dir_logs = "logs_simex_extract_serial_numbers_datetime_and_coordinates"
    logger = get_logger_for_writing_logs_to_file(input_directory,
                                                 dir_logs)
    input_directory_purepath = pathlib.PurePath(input_directory).name
    output_filename = os.path.join(input_directory,
                                   input_directory_purepath) + \
                                   "_simex_extract_serial_numbers_datetime_and_coordinates.json"
    logger.info("extraction of serial number, datetime and coordinates")
    logger.info("logs for extraction of serial number, datetime and coordinates in %s" % output_filename)

    dict_output = {}

    def extract_serial_number_of_file(filename, type_filename):
        logger.info("extraction of serial number of %s" % filename)
        serial_number = ""
        if type_filename == "audio":
            serial_number = read_metadata_audio.extract_serial_number(filename)
        else:
            if type_filename == "image":
                serial_number = read_metadata_image.extract_serial_number(filename)
        if not serial_number:
            logger.info("FAILED extraction of serial number of file")
            logger.info("returning empty serial number")
        else:
            logger.info("SUCCESSFUL extraction of serial number of %s" % filename)
        return serial_number

    def call_extract_serial_number_of_file_fun(dict_serial_number, filename):
        f_pathlib = pathlib.Path(filename)
        if f_pathlib.suffix in SUFFIXES_SIPECAM_AUDIO:
            dict_serial_number[filename] = extract_serial_number_of_file(filename, "audio")
        else:
            if f_pathlib.suffix in SUFFIXES_SIPECAM_IMAGES:
                dict_serial_number[filename] = extract_serial_number_of_file(filename, "image")

    def extract_serial_number_of_files(input_dir,
                                       mixed,
                                       d_output,
                                       d_serial_number):
        iterator = multiple_file_types(input_dir,
                                       *SUFFIXES_TARGET)
        if mixed:
            for f in iterator:
                call_extract_serial_number_of_file_fun(d_serial_number,
                                                       f)
                if d_serial_number[f]:
                    if d_serial_number[f] not in d_output["SerialNumber"].values():
                        d_output["SerialNumber"].update(d_serial_number)
        else:
            not_success = True
            while not_success:
                f = next(iterator)
                call_extract_serial_number_of_file_fun(d_serial_number,
                                                       f)
                if d_serial_number[f]:
                    not_success = False
                    d_output["SerialNumber"].update(d_serial_number)
        if len(d_output["SerialNumber"].keys()) < 1:
            logger.info("there were no serial numbers to extract")

    def extract_datetime(filename, type_filename):
        logger.info("extraction of datetime of %s" % filename)
        datetime_of_file = ""
        if type_filename == "audio":
            datetime_of_file = read_metadata_audio.extract_datetime_original(filename)
        else:
            if type_filename == "image":
                datetime_of_file = read_metadata_image.extract_datetime_original(filename)
        if not datetime_of_file:
            logger.info("FAILED extraction of datetime of file")
            logger.info("returning empty datetime")
        else:
            logger.info("SUCCESSFUL extraction of datetime of %s" % filename)
        return datetime_of_file

    def call_extract_datetime_fun(dict_datetime, filename):
        f_pathlib = pathlib.Path(filename)
        if f_pathlib.suffix in SUFFIXES_SIPECAM_AUDIO:
            dict_datetime[filename] = extract_datetime(filename, "audio")
        else:
            if f_pathlib.suffix in SUFFIXES_SIPECAM_IMAGES:
                dict_datetime[filename] = extract_datetime(filename, "image")

    def extract_datetime_of_files(input_dir,
                                  d_output,
                                  d_datetime):
        iterator = multiple_file_types(input_dir,
                                       *SUFFIXES_TARGET)
        for f in iterator:
            call_extract_datetime_fun(d_datetime,
                                      f)
            if d_datetime[f]:
                if d_datetime[f] not in d_output["Datetime"].values():
                    d_output["Datetime"].update(d_datetime)

        if len(d_output["Datetime"].keys()) < 1:
            logger.info("there were no dates to extract")

        def order_dict_datetime():
            return {k: v for k, v in sorted(d_output["Datetime"].items(),
                                            key=itemgetter(1))}


        def extract_first_last_dates_and_difference():
            if len(d_output["Datetime"].keys()) >= 2:
                first_key, *_, last_key = d_output["Datetime"].keys()
                d1 = d_output["Datetime"][first_key]
                d2 = d_output["Datetime"][last_key]
                d_output["Datetime"] = {first_key: d1,
                                        last_key : d2
                                       }
                format_string_data = "%Y-%m-%d"
                d1_datetime = datetime.datetime.strptime(d1,
                                                         format_string_data)
                d2_datetime = datetime.datetime.strptime(d2,
                                                         format_string_data)
                diff_datetimes = d2_datetime - d1_datetime
                d_output["DaysBetweenFirstAndLastDate"] = diff_datetimes.days

        if not mixed:
            d_output["Datetime"] = order_dict_datetime()
            extract_first_last_dates_and_difference()

    with open(output_filename, "w") as dst:
        dict_output["SerialNumber"] = {}
        dict_output["Coordinates"] = {}
        dict_output["Datetime"] = {}
        dict_serial_number = {}
        dict_datetime = {}
        extract_serial_number_of_files(input_directory,
                                       mixed,
                                       dict_output,
                                       dict_serial_number)
        extract_datetime_of_files(input_directory,
                                  dict_output,
                                  dict_datetime)

        json.dump(dict_output, dst)

