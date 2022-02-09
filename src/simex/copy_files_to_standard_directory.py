import os
import argparse
import json
import pathlib
import datetime

from simex import get_logger_for_writing_logs_to_file
from simex.utils.zendro import query_for_copy_files_to_standard_directory

def arguments_parse():
    help = """
Copy files to directory of server. Path that will have the files is created
according to:
id_cumulus/node_nomenclature/date_of_device_deployment/type_of_device/uuid.(JPG|WAV|AVI)

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
    args = parser.parse_args()
    return args


def main():
    args = arguments_parse()
    directory_with_file_of_serial_number_and_dates = args.directory_with_file_of_serial_number_and_dates
    filename_for_logs = "logs_simex_copy_files_to_standard_directory"
    logger = get_logger_for_writing_logs_to_file(directory_with_file_of_serial_number_and_dates,
                                                 filename_for_logs)
    input_directory_purepath = pathlib.PurePath(directory_with_file_of_serial_number_and_dates).name
    file_with_serial_number_and_dates = os.path.join(directory_with_file_of_serial_number_and_dates,
                                                         input_directory_purepath) + \
                                                         "_simex_extract_serial_numbers_datetimes.json"

    with open(file_with_serial_number_and_dates, 'r') as f:
        dict_source = json.load(f)

    dict_source_serial_number = dict_source["SerialNumber"]
    dict_source_dates = dict_source["Datetimes"]
    diff_dates = dict_source["DaysBetweenFirstAndLastDatetime"]

    filename_source, serial_number = tuple(dict_source_serial_number.items())[0]

    logger.info("File %s has serial number %s" % (filename_source, serial_number))
    
    tup_source_dates = tuple(dict_source_dates.items())
    
    filename_source_first_date,  first_date_str  = tup_source_dates[0]
    filename_source_second_date, second_date_str = tup_source_dates[1]

    logger.info("File %s has datetime %s" % (filename_source_first_date,
                                             first_date_str))
    logger.info("File %s has datetime %s" % (filename_source_second_date,
                                             second_date_str))

    logger.info("DaysBetweenFirstAndLastDatetime: %s" % diff_dates)

    query_result, operation_sgqlc = query_for_copy_files_to_standard_directory(serial_number,
                                                                               first_date_str,
                                                                               second_date_str)
    logger.info("Query to Zendro GQL: %s" % operation_sgqlc)
    
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
        
    #list_dates_device_deployment = [d["date_deployment"].split('T')[0] for d in device_deploymentsFilter_list]
    
