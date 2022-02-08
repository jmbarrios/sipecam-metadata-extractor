import os
import argparse
import json
import pathlib
import datetime

from sgqlc.operation import Operation
from sgqlc.endpoint.http import HTTPEndpoint

from simex import get_logger_for_writing_logs_to_file
from simex.utils import zendro
from simex.sipecam_zendro_schema import sipecam_zendro_schema as schema

def arguments_parse():
    help = """
Extract metadata of file, fill fields of File model in
Zendro and copy file to directory of server. Write logs for each
step.

--------------
Example usage:
--------------

copy_files_to_standard_directory --directory_with_file_of_serial_number_and_datetimes /dir/filename.json

"""
    parser = argparse.ArgumentParser(description=help,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--directory_with_file_of_serial_number_and_datetimes",
                        required=True,
                        default=None,
                        help="Directory that has json file with serial number and datetimes")
    args = parser.parse_args()
    return args


def main():
    args = arguments_parse()
    directory_with_file_of_serial_number_and_datetimes = args.directory_with_file_of_serial_number_and_datetimes
    filename_for_logs = "logs_simex_copy_files_to_standard_directory"
    logger = get_logger_for_writing_logs_to_file(directory_with_file_of_serial_number_and_datetimes,
                                                 filename_for_logs)    
    input_directory_purepath = pathlib.PurePath(directory_with_file_of_serial_number_and_datetimes).name
    file_with_serial_number_and_datetimes = os.path.join(directory_with_file_of_serial_number_and_datetimes,
                                                         input_directory_purepath) + \
                                                         "_simex_extract_serial_numbers_datetime_and_coordinates.json"    

    with open(file_with_serial_number_and_datetimes, 'r') as f:
        dict_source = json.load(f)
    
    dict_source_serial_number = dict_source["SerialNumber"]
    dict_source_datetimes = dict_source["Datetimes"]
    diff_datetimes = dict_source["DaysBetweenFirstAndLastDatetime"]
    
    filename_source, serial_number = tuple(dict_source_serial_number.items())[0]
    
    logger.info("File %s has serial number %s" % (filename_source, serial_number))
        
    filename_source_first_datetime,  first_datetime  = tuple(dict_source_datetimes.items())[0]
    filename_source_second_datetime, second_datetime = tuple(dict_source_datetimes.items())[1]
    
    logger.info("File %s has datetime %s" % (filename_source_first_datetime, 
                                             first_datetime))
    logger.info("File %s has datetime %s" % (filename_source_second_datetime, 
                                             second_datetime))
        
    logger.info("DaysBetweenFirstAndLastDatetime: %s" % diff_datetimes)
    
    token = zendro.get_token()
    
    headers = {
        "Authorization": "Bearer " + token,
        "Accept": "application/json",
        'Content-Type': 'application/json; charset=utf-8'
    }
    
    endpoint = HTTPEndpoint(zendro.get_zendro_url_for_gql(),
                            headers)    
    op = Operation(schema.Query)
    op.physical_devices(pagination={"limit": 0},
                        search={"field": "serial_number", 
                                "value": serial_number, 
                                "operator": "like"})
    op.physical_devices.device_deployments_filter(pagination={"limit": 0}
                                                 ).date_deployment() #sgqlc selection type
    logger.info("Query to Zendro GQL: %s" % op)
    query_result = endpoint(op)
    device_deploymentsFilter = query_result["data"]["physical_devices"][0]["device_deploymentsFilter"]
    list_dates_device_deployment = [d["date_deployment"].split('T')[0] for d in device_deploymentsFilter]
    
    [logger.info(d) for d in list_dates_device_deployment]
    
    format_string_data = "%Y-%m-%d"
        
    list_datetimes_device_deployment = [datetime.datetime.strptime(d,
                                                                   format_string_data) for d in list_dates_device_deployment]
    
    
    [logger.info(d) for d in list_datetimes_device_deployment]