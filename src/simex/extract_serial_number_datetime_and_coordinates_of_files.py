import glob
import os
import argparse
import json
import pathlib
from operator import itemgetter
import datetime
from multiprocessing import Pool
from functools import reduce

from simex import get_logger_for_writing_logs_to_file
from simex import SUFFIXES_SIPECAM_AUDIO, SUFFIXES_SIPECAM_IMAGES
from simex.utils.directories_and_files import multiple_file_types
from simex import read_metadata_image, read_metadata_audio

SUFFIXES_TARGET = SUFFIXES_SIPECAM_AUDIO + SUFFIXES_SIPECAM_IMAGES

def extract_datetime(filename):
    """
    Helper function to extract datetime of file.
    It's outside main to execute it in parallel.
    """
    f_pathlib = pathlib.Path(filename)
    datetime_of_file = ""
    if f_pathlib.suffix in SUFFIXES_SIPECAM_AUDIO:
        datetime_of_file = read_metadata_audio.extract_datetime_original(filename)
    else:
        if f_pathlib.suffix in SUFFIXES_SIPECAM_IMAGES:
            datetime_of_file = read_metadata_image.extract_datetime_original(filename)
    return {filename: datetime_of_file}


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
    parser.add_argument('--parallel',
                    action='store_true',
                    help='Execution in parallel?')
    parser.add_argument("--number_of_processes",
                        required=False,
                        type=int,
                        default=None,
                        help="Select number of processes for parallel execution")
    args = parser.parse_args()
    return args

def main():
    args = arguments_parse()
    input_directory = args.input_directory
    mixed = args.mixed
    parallel = args.parallel
    number_of_processes = args.number_of_processes
    filename_for_logs = "logs_simex_extract_serial_numbers_datetime_and_coordinates"
    logger = get_logger_for_writing_logs_to_file(input_directory,
                                                 filename_for_logs)
    input_directory_purepath = pathlib.PurePath(input_directory).name
    output_filename = os.path.join(input_directory,
                                   input_directory_purepath) + \
                                   "_simex_extract_serial_numbers_datetime_and_coordinates.json"
    logger.info("extraction of serial number, datetime and coordinates")
    logger.info("logs for extraction of serial number, datetime and coordinates in %s" % output_filename)

    dict_output = {}

    if number_of_processes and not parallel:
        parallel = True

    def extract_serial_number(filename):
        """
        Helper function to extract serial number of file.
        """
        f_pathlib = pathlib.Path(filename)
        logger.info("extraction of serial number of %s" % filename)
        serial_number = ""
        if f_pathlib.suffix in SUFFIXES_SIPECAM_AUDIO:
            serial_number = read_metadata_audio.extract_serial_number(filename)
        else:
            if f_pathlib.suffix in SUFFIXES_SIPECAM_IMAGES:
                serial_number = read_metadata_image.extract_serial_number(filename)
        if not serial_number:
            logger.info("FAILED extraction of serial number of file")
            logger.info("returning empty serial number")
        else:
            logger.info("SUCCESSFUL extraction of serial number of %s" % filename)
        return serial_number

    def extract_serial_number_of_files(input_dir,
                                       mixed,
                                       d_output,
                                       d_serial_number):
        iterator = multiple_file_types(input_dir,
                                       *SUFFIXES_TARGET)
        if mixed: #directory with files from several devices.
            for f in iterator:
                d_serial_number[f] = extract_serial_number(f)
                if d_serial_number[f]:
                    d_output["SerialNumber"].update(d_serial_number)
        else:
            not_success = True
            while not_success:
                f = next(iterator)
                d_serial_number[f] = extract_serial_number(f)
                if d_serial_number[f]:
                    not_success = False
                    d_output["SerialNumber"].update(d_serial_number)
        if len(d_output["SerialNumber"].keys()) < 1:
            logger.info("there were no serial numbers to extract")

    def extract_datetime_of_files(input_dir,
                                  d_output,
                                  d_datetime,
                                  number_of_processes=4):
        iterator = multiple_file_types(input_dir,
                                       *SUFFIXES_TARGET)

        if parallel:
            with Pool(processes=number_of_processes) as pool:
                res_map = pool.map(extract_datetime,
                                   iterator) #returns list of dictionaries
                for dictionary in res_map:
                    filename, datetime_file = tuple(dictionary.items())[0]
                    logger.info("extraction of datetime of %s" % filename)
                    if not datetime_file:
                        logger.info("FAILED extraction of datetime of file %s" % filename)
                        logger.info("returning empty datetime")
                    else:
                        logger.info("SUCCESSFUL extraction of datetime of %s" % filename)
                #see: https://stackoverflow.com/questions/3494906/how-do-i-merge-a-list-of-dicts-into-a-single-dict
                d_output["Datetimes"] = reduce(lambda a, b: {**a, **b}, res_map)
        else:
            for filename in iterator:
                logger.info("extraction of datetime of %s" % filename)
                res_extract_datetime = extract_datetime(filename)
                datetime_file = res_extract_datetime[filename]
                if not datetime_file:
                    logger.info("FAILED extraction of datetime of file %s" % filename)
                    logger.info("returning empty datetime")
                else:
                    logger.info("SUCCESSFUL extraction of datetime of %s" % filename)
                    d_output["Datetimes"].update(res_extract_datetime)

        if len(d_output["Datetimes"].keys()) < 1:
            logger.info("there were no dates to extract")

        def order_dict_datetime():
            """
            Helper function to order dictionary Datetime using datetimes.
            """
            return {k: v for k, v in sorted(d_output["Datetimes"].items(),
                                            key=itemgetter(1))}

        def extract_first_last_dates_and_difference():
            """
            Helper function to simplify dictionary Datetime with
            only first, last and if there are more than two datetimes then
            computes difference between first and last datetimes in days.
            """
            if len(d_output["Datetimes"].keys()) >= 2:
                first_key, *_, last_key = d_output["Datetimes"].keys()
                d1_str = d_output["Datetimes"][first_key]
                d2_str = d_output["Datetimes"][last_key]
                d_output["Datetimes"] = {first_key: d1_str,
                                        last_key : d2_str
                                       }
                format_string_data = "%Y-%m-%d"
                d1_datetime = datetime.datetime.strptime(d1_str,
                                                         format_string_data)
                d2_datetime = datetime.datetime.strptime(d2_str,
                                                         format_string_data)
                diff_datetimes = d2_datetime - d1_datetime
                d_output["DaysBetweenFirstAndLastDatetime"] = diff_datetimes.days

        if not mixed: #directory with files from one device.
            d_output["Datetimes"] = order_dict_datetime()
            extract_first_last_dates_and_difference()

    with open(output_filename, "w") as dst:
        dict_output["SerialNumber"] = {}
        dict_output["Coordinates"] = {}
        dict_output["Datetimes"] = {}
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

