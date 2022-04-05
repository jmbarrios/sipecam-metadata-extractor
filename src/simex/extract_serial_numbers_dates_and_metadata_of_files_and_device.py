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
from simex import SUFFIXES_SIPECAM, SUFFIXES_SIPECAM_AUDIO, \
SUFFIXES_SIPECAM_IMAGES, SUFFIXES_SIPECAM_VIDEO
from simex.utils.directories_and_files import multiple_file_types
from simex import read_metadata_image, read_metadata_video, read_metadata_audio

SUFFIXES_AUDIO_IMAGES = SUFFIXES_SIPECAM_AUDIO + SUFFIXES_SIPECAM_IMAGES

def extract_metadata(filename):
    """
    Helper function to extract date and metadata of file.
    Is outside main to execute it in parallel.
    """
    f_pathlib = pathlib.Path(filename)
    date_of_file = ""
    if f_pathlib.suffix in SUFFIXES_SIPECAM_AUDIO:
        date_of_file = read_metadata_audio.extract_date(filename)
        tuple_metadata_of_file = (filename,read_metadata_audio.get_metadata_of_file(filename))
    else:
        if f_pathlib.suffix in SUFFIXES_SIPECAM_IMAGES:
            date_of_file = read_metadata_image.extract_date(filename)
            tuple_metadata_of_file = (filename,read_metadata_image.get_metadata_of_file(filename))
        else:
            if f_pathlib.suffix in SUFFIXES_SIPECAM_VIDEO:
                date_of_file = read_metadata_video.extract_date(filename)
                tuple_metadata_of_file = (filename,read_metadata_video.get_metadata_of_file(filename))
    tuple_date = (filename, date_of_file)

    return (tuple_date, tuple_metadata_of_file)


def arguments_parse():
    help = """
Traverse files in a directory to extract their serial number and dates.
--------------
Example usage:
--------------
extract_serial_numbers_dates_and_metadata_of_files_and_device --input_dir /dir/
"""


    parser = argparse.ArgumentParser(description=help,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--input_directory",
                        required=True,
                        default=None,
                        help="Directory with WAV, JPG and AVI files")
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
    parallel = args.parallel
    number_of_processes = args.number_of_processes
    filename_for_logs = "logs_simex_extract_serial_numbers_dates_and_metadata_of_files_and_device"
    logger = get_logger_for_writing_logs_to_file(input_directory,
                                                 filename_for_logs)
    input_directory_purepath = pathlib.PurePath(input_directory).name
    output_filename = os.path.join(input_directory,
                                   input_directory_purepath) + \
                                   "_simex_extract_serial_numbers_dates_and_metadata_of_files_and_device.json"
    pathlib.Path(output_filename).unlink(missing_ok=True) #remove in case it exists
    logger.info("extraction of serial_numbers_dates_and_metadata_of_files_and_device")
    logger.info("logs for extraction of serial_numbers_dates_and_metadata_of_files_and_device in %s" % output_filename)

    dict_output = {}

    if number_of_processes and not parallel:
        parallel = True

    def extract_metadata_of_device(filename):
        """
        Helper function to extract serial number of file.
        """
        f_pathlib = pathlib.Path(filename)
        if f_pathlib.suffix in SUFFIXES_SIPECAM_AUDIO:
            dict_metadata_of_device = read_metadata_audio.get_metadata_of_device(filename)
        else:
            if f_pathlib.suffix in SUFFIXES_SIPECAM_IMAGES:
                dict_metadata_of_device = read_metadata_image.get_metadata_of_device(filename)
        return dict_metadata_of_device

    def extract_metadata_of_device_from_files(input_dir,
                                              d_output):
        iterator = multiple_file_types(input_dir,
                                       SUFFIXES_AUDIO_IMAGES)
        not_success = True
        while not_success:
            try:
                filename = next(iterator)
                logger.info("extraction of metadata of device from %s" % filename)
                res_extract_metadata_of_device = extract_metadata_of_device(filename)
                serial_number_file = res_extract_metadata_of_device["SerialNumber"]
                if serial_number_file:
                    logger.info("SUCCESSFUL extraction of serial number of %s" % filename)
                    not_success = False
                    d_output["MetadataDevice"] = res_extract_metadata_of_device
            except Exception as e:
                logger.info(e)
                logger.info("there were no audios nor images found in dir: %s, serial number can not be retrieved from " % input_dir)
                not_success = False
        #as videos have no coordinates in d_output["GPSFile"] for images they will be saved
        f_pathlib = pathlib.Path(filename)
        if f_pathlib.suffix in SUFFIXES_SIPECAM_IMAGES:
            d_output["GPSFile"] = read_metadata_image.extract_gps(filename)
            if not d_output["GPSFile"]["GPSLatitudeRef"]: #check if extraction of GPS information was successful
                logger.info("there were no GPS metadata associated with file %s, returning empty string" % filename)

    def extract_metadata_of_files(input_dir,
                                  d_output,
                                  d_gps_for_videos,
                                  number_of_processes=4):
        iterator = multiple_file_types(input_dir,
                                       SUFFIXES_SIPECAM)
        d_output["Dates"] = {}
        d_output["MetadataFiles"] = {}

        if parallel:
            with Pool(processes=number_of_processes) as pool:
                res_map = pool.map(extract_metadata,
                                   iterator) #returns list of tuples. Each element of tuple is another tuple
                for t in res_map:
                    filename, date_file = t[0] #t[0] tuple with filename and date as 1st, 2nd elements resp
                    logger.info("extraction of date of %s" % filename)
                    if not date_file:
                        logger.info("FAILED extraction of date of file %s" % filename)
                        logger.info("returning empty date")
                    else:
                        logger.info("SUCCESSFUL extraction of date of %s" % filename)
                        d_output["Dates"][filename] = date_file
                        filename, metadata_file = t[1] #t[1] tuple with filename and metadata as 1st, 2nd elements resp
                        d_output["MetadataFiles"][filename] = metadata_file
                        f_pathlib = pathlib.Path(filename)
                        if f_pathlib.suffix in SUFFIXES_SIPECAM_IMAGES:
                            if not metadata_file["GPSLatitudeRef"]:
                                logger.info("there were no GPS metadata associated with file %s, returning empty string" % filename)
                        #as videos have no coordinates variable d_gps_for_videos will be used to assign them
                        if f_pathlib.suffix in SUFFIXES_SIPECAM_VIDEO:
                            d_output["MetadataFiles"][filename]["GPSLatitudeRef"]  = d_gps_for_videos["GPSLatitudeRef"]
                            d_output["MetadataFiles"][filename]["GPSLongitudeRef"] = d_gps_for_videos["GPSLongitudeRef"]
                            d_output["MetadataFiles"][filename]["GPSLatitude"]     = d_gps_for_videos["GPSLatitude"]
                            d_output["MetadataFiles"][filename]["GPSLongitude"]    = d_gps_for_videos["GPSLongitude"]
        else:
            for filename in iterator:
                logger.info("extraction of date of %s" % filename)
                tuple_date, tuple_metadata_of_file = extract_metadata(filename)
                date_file = tuple_date[1] #tuple with filename and date as 1st and 2nd elements resp
                if not date_file:
                    logger.info("FAILED extraction of date of file %s" % filename)
                    logger.info("returning empty date")
                else:
                    logger.info("SUCCESSFUL extraction of date of %s" % filename)
                    d_output["Dates"][filename] = date_file
                    metadata_file = tuple_metadata_of_file[1] #tuple with filename and metadata as 1st and 2nd elements resp
                    d_output["MetadataFiles"][filename] = metadata_file
                    f_pathlib = pathlib.Path(filename)
                    if f_pathlib.suffix in SUFFIXES_SIPECAM_IMAGES and not metadata_file["GPSLatitudeRef"]:
                        logger.info("there were no GPS metadata associated with file %s, returning empty string" % filename)
                    if f_pathlib.suffix in SUFFIXES_SIPECAM_VIDEO:
                        d_output["MetadataFiles"][filename]["GPSLatitudeRef"]  = d_gps_for_videos["GPSLatitudeRef"]
                        d_output["MetadataFiles"][filename]["GPSLongitudeRef"] = d_gps_for_videos["GPSLongitudeRef"]
                        d_output["MetadataFiles"][filename]["GPSLatitude"]     = d_gps_for_videos["GPSLatitude"]
                        d_output["MetadataFiles"][filename]["GPSLongitude"]    = d_gps_for_videos["GPSLongitude"]

        if len(d_output["Dates"].keys()) < 1:
            logger.info("there were no dates to extract")

        def order_dict_dates():
            """
            Helper function to order dictionary Dates using dates.
            """
            return {k: v for k, v in sorted(d_output["Dates"].items(),
                                            key=itemgetter(1))}

        def extract_first_last_dates_and_difference():
            """
            Helper function to simplify dictionary Dates with
            only first, last and if there are more than two dates then
            computes difference between first and last dates in days.
            """
            first_key, *_, last_key = d_output_dates_keys
            d1_str = d_output["Dates"][first_key]
            d2_str = d_output["Dates"][last_key]
            d_output["FirstAndLastDate"] = {first_key: d1_str,
                                            last_key : d2_str
                                            }
            format_string_data = "%Y-%m-%d"
            d1_datetime = datetime.datetime.strptime(d1_str,
                                                     format_string_data)
            d2_datetime = datetime.datetime.strptime(d2_str,
                                                     format_string_data)
            diff_datetimes = d2_datetime - d1_datetime
            diff_datetimes_days = diff_datetimes.days
            #there are devices that were placed only 1 day, thereby diff_datetimes_days = 0
            if diff_datetimes_days == 0:
                diff_datetimes_days = 1
            d_output["DaysBetweenFirstAndLastDate"] = diff_datetimes_days
            del d_output["Dates"]

        d_output["Dates"] = order_dict_dates()
        d_output_dates_keys = d_output["Dates"].keys()

        if len(d_output_dates_keys) >= 2:
            extract_first_last_dates_and_difference()
        #there are devices that were placed only 1 day
        if len(d_output_dates_keys) == 1:
            only_key = list(d_output_dates_keys)[0]
            d1_str = d_output["Dates"][only_key]
            format_string_data = "%Y-%m-%d"
            d1_datetime = datetime.datetime.strptime(d1_str,
                                                     format_string_data)
            diff_dates = 1
            diff_dates_datetime = datetime.timedelta(diff_dates)
            d2_datetime = d1_datetime + diff_dates_datetime
            d2_str = datetime.datetime.strftime(d2_datetime, format_string_data)
            d_output["FirstAndLastDate"] = {only_key: d1_str,
                                            only_key: d2_str
                                           }
            d_output["DaysBetweenFirstAndLastDate"] = 1
            del d_output["Dates"]

    with open(output_filename, "w") as dst:
        dict_output = {}
        dict_gps_for_videos = {}
        extract_metadata_of_device_from_files(input_directory,
                                              dict_output)
        try:
            dict_gps_for_videos = dict_output["GPSFile"]
        except Exception as e:
            logger.info("GPSFile key not found for videos, files from directory are of audio")
        extract_metadata_of_files(input_directory,
                                  dict_output,
                                  dict_gps_for_videos)
        try:
            del dict_output["GPSFile"]
        except Exception as e:
            logger.info("GPSFile key not found for videos, files from directory are of audio")
        json.dump(dict_output, dst)
