import os
import argparse
import json
import pathlib
import datetime
import shutil

from simex import get_logger_for_writing_logs_to_file
from simex.utils.zendro import query_for_copy_files_to_standard_directory, \
query_alternative_auxiliar_for_copy_files_to_standard_directory, \
query_alternative_for_copy_files_to_standard_directory
from simex.utils.directories_and_files import multiple_file_types
from simex import SUFFIXES_SIPECAM_AUDIO, SUFFIXES_SIPECAM_IMAGES, SUFFIXES_SIPECAM_VIDEO

SUFFIXES_TARGET = SUFFIXES_SIPECAM_AUDIO + SUFFIXES_SIPECAM_IMAGES + SUFFIXES_SIPECAM_VIDEO

def arguments_parse():
    help = """
Copy files to directory of server. Path that will have the files is created
according to:
cumulus_name/node_nomenclature/date_of_device_deployment/type_of_device/uuid.(JPG|WAV|AVI)

--------------
Example usage:
--------------

copy_files_to_standard_directory --directory_with_file_of_serial_number_and_dates /dir/filename.json

"""
    parser = argparse.ArgumentParser(description=help,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--directory_with_file_of_serial_number_and_dates",
                        required=True,
                        default=None,
                        help="Directory that has json file with serial number and dates")
    parser.add_argument("--path_for_standard_directory",
                        required=True,
                        default=None,
                        help="Directory that has json file with serial number and dates")
    args = parser.parse_args()
    return args


def main():
    args = arguments_parse()
    directory_with_file_of_serial_number_and_dates = args.directory_with_file_of_serial_number_and_dates
    path_for_standard_directory = args.path_for_standard_directory
    filename_for_logs = "logs_simex_copy_files_to_standard_directory"
    logger = get_logger_for_writing_logs_to_file(directory_with_file_of_serial_number_and_dates,
                                                 filename_for_logs)
    input_directory_purepath = pathlib.PurePath(directory_with_file_of_serial_number_and_dates).name
    file_with_serial_number_and_dates = os.path.join(directory_with_file_of_serial_number_and_dates,
                                                         input_directory_purepath) + \
                                                         "_simex_extract_serial_numbers_dates.json"

    with open(file_with_serial_number_and_dates, 'r') as f:
        dict_source = json.load(f)

    dict_source_serial_number = dict_source["SerialNumber"]
    dict_source_dates = dict_source["FirstAndLastDate"]
    diff_dates = dict_source["DaysBetweenFirstAndLastDate"]

    filename_source_serial_number, serial_number = tuple(dict_source_serial_number.items())[0]

    logger.info("File %s has serial number %s" % (filename_source_serial_number,
                                                  serial_number))

    tup_source_dates = tuple(dict_source_dates.items())

    filename_source_first_date,  first_date_str  = tup_source_dates[0]
    filename_source_second_date, second_date_str = tup_source_dates[1]

    logger.info("File %s has date %s" % (filename_source_first_date,
                                             first_date_str))
    logger.info("File %s has date %s" % (filename_source_second_date,
                                             second_date_str))

    logger.info("DaysBetweenFirstAndLastDate: %s" % diff_dates)

    filename_source_serial_number_pathlib = pathlib.Path(filename_source_serial_number)

    if filename_source_serial_number_pathlib.suffix in SUFFIXES_SIPECAM_AUDIO:
        query_result, operation_sgqlc = query_for_copy_files_to_standard_directory(serial_number,
                                                                                   first_date_str,
                                                                                   second_date_str,
                                                                                   file_type="audio")
    else:
        if filename_source_serial_number_pathlib.suffix in SUFFIXES_SIPECAM_IMAGES:
            query_result, operation_sgqlc = query_for_copy_files_to_standard_directory(serial_number,
                                                                                       first_date_str,
                                                                                       second_date_str,
                                                                                       file_type="image")
        else:
            if filename_source_serial_number_pathlib.suffix in SUFFIXES_SIPECAM_VIDEO:
                query_result, operation_sgqlc = query_for_copy_files_to_standard_directory(serial_number,
                                                                                           first_date_str,
                                                                                           second_date_str,
                                                                                           file_type="video")

    logger.info("Query to Zendro GQL: %s" % operation_sgqlc)

    def copy_files_to_standard_dir(src_dir, dst_dir):
        iterator = multiple_file_types(src_dir,
                                       SUFFIXES_TARGET)
        for filename in iterator:
            f_pathlib = pathlib.Path(filename)
            if f_pathlib.suffix in SUFFIXES_SIPECAM_AUDIO:
                standard_dir = os.path.join(dst_dir,
                                            "audios",
                                            f_pathlib.parent.name)
                logger.info("File %s will be copied to: %s" % (filename, standard_dir))
            else:
                if f_pathlib.suffix in SUFFIXES_SIPECAM_IMAGES:
                    standard_dir = os.path.join(dst_dir,
                                                "images")
                    logger.info("File %s will be copied to: %s" % (filename, standard_dir))

                else:
                    if f_pathlib.suffix in SUFFIXES_SIPECAM_VIDEO:
                        standard_dir = os.path.join(dst_dir,
                                                    "videos")
                        logger.info("File %s will be copied to: %s" % (filename, standard_dir))

    try:
        device_deploymentsFilter_list = query_result["data"]["physical_devices"][0]["device_deploymentsFilter"]
        if len(device_deploymentsFilter_list) == 1:
            device_deploymentsFilter_dict = device_deploymentsFilter_list[0]
            nomenclature_node  = device_deploymentsFilter_dict["node"]["nomenclatura"]
            cumulus_name       = device_deploymentsFilter_dict["cumulus"]["name"]
            date_of_deployment = device_deploymentsFilter_dict["date_deployment"].split('T')[0]
            logger.info("SUCCESSFUL extraction of nomenclature of node, cumulus name and date of deployment")
            logger.info("directory %s has nom node: %s, cum name: %s, date of depl: %s" % (directory_with_file_of_serial_number_and_dates,
                                                                                           nomenclature_node,
                                                                                           cumulus_name,
                                                                                           date_of_deployment)
                       )
            path_with_files_copied = os.path.join(path_for_standard_directory,
                                                  cumulus_name,
                                                  nomenclature_node,
                                                  serial_number,
                                                  date_of_deployment)
            logger.info("path where files will be copied: %s" % path_with_files_copied)
            os.makedirs(path_with_files_copied, exist_ok=True)
            copy_files_to_standard_dir(directory_with_file_of_serial_number_and_dates,
                                       path_with_files_copied)

        else:
            if len(device_deploymentsFilter_list) == 0: #make another query as first_date_str could be greater than date of deployment of device
                logger.info("last query wasn't successful")
                query_result, operation_sgqlc = query_alternative_auxiliar_for_copy_files_to_standard_directory(serial_number)
                logger.info("Query alternative auxiliar to Zendro GQL: %s" % operation_sgqlc)
                try:
                    device_deploymentsFilter_list = query_result["data"]["physical_devices"][0]["device_deploymentsFilter"]
                    format_string_data = "%Y-%m-%d"
                    list_dates_device_deployment = [d["date_deployment"].split('T')[0] for d in device_deploymentsFilter_list]
                    list_datetimes_device_deployment = [datetime.datetime.strptime(d["date_deployment"].split('T')[0],
                                                                                   format_string_data) for d in device_deploymentsFilter_list]
                    first_datetime  = datetime.datetime.strptime(first_date_str, format_string_data)
                    second_datetime = datetime.datetime.strptime(second_date_str, format_string_data)
                    diff_dates_datetime = datetime.timedelta(diff_dates)
                    list_datetimes_device_deployment_increased = [d + diff_dates_datetime/2 for d in list_datetimes_device_deployment]
                    k = 0
                    for datetimes_device_deployment in list_datetimes_device_deployment_increased:
                        if first_datetime <= datetimes_device_deployment and datetimes_device_deployment <= second_datetime:
                            idx_date = k
                        k += 1
                    date_for_filter = device_deploymentsFilter_list[idx_date]["date_deployment"]
                    query_result, operation_sgqlc = query_alternative_for_copy_files_to_standard_directory(serial_number,
                                                                                                           date_for_filter)
                    logger.info("Query alternative to Zendro GQL: %s" % operation_sgqlc)
                    try:
                        device_deploymentsFilter_list = query_result["data"]["physical_devices"][0]["device_deploymentsFilter"]
                        device_deploymentsFilter_dict = device_deploymentsFilter_list[0]
                        nomenclature_node  = device_deploymentsFilter_dict["node"]["nomenclatura"]
                        cumulus_name       = device_deploymentsFilter_dict["cumulus"]["name"]
                        date_of_deployment = list_dates_device_deployment[idx_date]
                        logger.info("SUCCESSFUL extraction of nomenclature of node, cumulus name and date of deployment")
                        logger.info("directory %s has nom node: %s, cum name: %s, date of depl: %s" % (directory_with_file_of_serial_number_and_dates,
                                                                                                       nomenclature_node,
                                                                                                       cumulus_name,
                                                                                                       date_of_deployment)
                                   )
                    except Exception as e:
                        logger.info(e)
                        logger.info("unsuccessful query %s" % operation_sgqlc)
                except Exception as e:
                    logger.info(e)
                    logger.info("unsuccessful query %s" % operation_sgqlc)
            else: #len of list is >=1 then there's no unique date of deployment of device
                logger.info("There's no unique date of deployment and can not select one date to create standard directory")
    except Exception as e:
        logger.info(e)
        logger.info("unsuccessful query %s" % operation_sgqlc)
