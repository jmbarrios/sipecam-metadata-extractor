import os
import re
import argparse
import pathlib
import json
import datetime

from shapely.geometry import Point, Polygon

from simex import get_logger_for_writing_logs_to_file
from simex.utils.directories_and_files import multiple_file_types
from simex.utils.zendro import query_for_extend_metadata_of_files
from simex import SUFFIXES_SIPECAM_AUDIO, SUFFIXES_SIPECAM_IMAGES, SUFFIXES_SIPECAM_VIDEO

def build_polygon_for_cumulus_geometry(cumulus_geom_coordinates):
    geom = []
    for point in cumulus_geom_coordinates:
        geom.append((point[1],point[0]))
    poly = Polygon(geom)
    return poly

def check_if_point_is_in_cumulus_geom(lat,lng, poly):
    point_to_check = Point(lat,lng)
    if point_to_check.within(poly.buffer(0.2)):
        return (lat, lng)
    else:
        return None

def arguments_parse():
    help = """
Traverse files in a directory to extend metadata of files

--------------
Example usage:
--------------

extend_metadata_of_files --input_directory /dir/

"""


    parser = argparse.ArgumentParser(description=help,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--input_directory",
                        required=True,
                        default=None,
                        help="Directory with JPG, AVI, WAV files")
    args = parser.parse_args()
    return args

def main():
    args = arguments_parse()
    input_directory = args.input_directory
    filename_for_logs = "logs_simex_extend_metadata_of_files"
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
    file_with_metadata_source =os.path.join(input_directory,
                                            input_directory_name + \
                                            "_simex_metadata_files_and_device_" + \
                                            last_date + \
                                            ".json")
    logger.info("Json file that will be the source: %s" % file_with_metadata_source)

    with open(file_with_metadata_source, 'r') as f:
        dict_source = json.load(f)
    serial_number   = dict_source["MetadataDevice"]["SerialNumber"]
    date_deployment = dict_source["MetadataDevice"]["DateDeployment"]
    lat_device      = dict_source["MetadataDevice"]["Latitude"]
    long_device     = dict_source["MetadataDevice"]["Longitude"]
    diff_dates      = dict_source["DaysBetweenFirstAndLastDate"]

    diff_dates_datetime = datetime.timedelta(diff_dates)
    format_string_data = "%Y-%m-%d"
    date_deployment_datetime = datetime.datetime.strptime(date_deployment,
                                                          format_string_data)
    date_retrieve_device = datetime.datetime.strftime(date_deployment_datetime + diff_dates_datetime,
                                                      format_string_data)
    first_key, *_, last_key = dict_source["MetadataFiles"] #first_key refers to filename
    filename_source_first_key_pathlib = pathlib.Path(first_key)
    if filename_source_first_key_pathlib.suffix in SUFFIXES_SIPECAM_AUDIO:
        type_files_in_dir = "audios"
        query_result, operation_sgqlc = query_for_extend_metadata_of_files(serial_number,
                                                                           date_deployment,
                                                                           date_retrieve_device,
                                                                           file_type="audio")
    else:
        if filename_source_first_key_pathlib.suffix in SUFFIXES_SIPECAM_IMAGES:
            type_files_in_dir = "images"
            query_result, operation_sgqlc = query_for_extend_metadata_of_files(serial_number,
                                                                               date_deployment,
                                                                               date_retrieve_device,
                                                                               file_type="image")
        else:
            if filename_source_first_key_pathlib.suffix in SUFFIXES_SIPECAM_VIDEO:
                type_files_in_dir = "videos"
                query_result, operation_sgqlc = query_for_extend_metadata_of_files(serial_number,
                                                                                   date_deployment,
                                                                                   date_retrieve_device,
                                                                                   file_type="video")
    logger.info("Query to Zendro GQL: %s" % operation_sgqlc)
    try:
        device_deploymentsFilter_list = query_result["data"]["physical_devices"][0]["device_deploymentsFilter"]
        if len(device_deploymentsFilter_list) == 1:
            logger.info("SUCCESSFUL extraction of geometry of cumulus")
            device_deploymentsFilter_dict = device_deploymentsFilter_list[0]
            cumulus_geometry = device_deploymentsFilter_dict["cumulus"]["geometry"]
            cumulus_geom_coordinates = cumulus_geometry["coordinates"][0]
            #compute centroid of cumulus, this will be the extension for metadata files and useful for masking
            cumulus_poly = build_polygon_for_cumulus_geometry(cumulus_geom_coordinates)
            lat_centroid_cumulus  = round(cumulus_poly.centroid.x, 5)
            long_centroid_cumulus = round(cumulus_poly.centroid.y, 5)
            logger.info("Centroid of cumulus, lat: %s, long: %s" %(lat_centroid_cumulus,
                                                                   long_centroid_cumulus))
            logger.info("Writing lat long of centroid for MetadataDevice")
            dict_source["MetadataDevice"]["CentroidCumulusLatitude"]  = lat_centroid_cumulus
            dict_source["MetadataDevice"]["CentroidCumulusLongitude"] = long_centroid_cumulus
            #validate lat long of device are correct
            logger.info("Validating lat and long of device are correct")
            t_lat_long_device = check_if_point_is_in_cumulus_geom(lat_device,
                                                                  long_device, 
                                                                  cumulus_poly)
            if t_lat_long_device:
                logger.info("Latitude and Longitude of device are in cumulus geometry")
                lat_device  = t_lat_long_device[0]
                long_device = t_lat_long_device[1]
            else:
                logger.info("Latitude and Longitude of device are not in cumulus geometry, returning None")
                lat_device  = None
                long_device = None
            dict_source["MetadataDevice"]["Latitude"]  = lat_device
            dict_source["MetadataDevice"]["Longitude"] = long_device

            for filename, metadata_file in dict_source["MetadataFiles"].items():
                if type_files_in_dir == "images" or type_files_in_dir == "videos":
                    lat_file  = dict_source["MetadataFiles"][filename]["GPSLatitude"]
                    long_file = dict_source["MetadataFiles"][filename]["GPSLongitude"]
                else:
                    if type_files_in_dir == "audios":
                        lat_file  = dict_source["MetadataFiles"][filename]["Latitude"]
                        long_file = dict_source["MetadataFiles"][filename]["Longitude"]
                #validate lat long of fil are correct
                logger.info("Validating lat and long of file are correct")
                t_lat_long_file = check_if_point_is_in_cumulus_geom(lat_file,
                                                                    long_file, 
                                                                    cumulus_poly)
                if t_lat_long_file:
                    logger.info("Latitude and Longitude of file are in cumulus geometry")
                    lat_file  = t_lat_long_file[0]
                    long_file = t_lat_long_file[1]
                    #check if lat long of device are None and use lat long of file to fill them
                    if not dict_source["MetadataDevice"]["Latitude"] and not dict_source["MetadataDevice"]["Longitude"]:
                        logger.info("Using lat long of file to fill lat long of device")
                        dict_source["MetadataDevice"]["Latitude"]  = lat_file
                        dict_source["MetadataDevice"]["Longitude"] = long_file       
                else:
                    logger.info("Latitude and Longitude of file are not in cumulus geometry, returning None")
                    #if lat long of file are None then use lat long of device.
                    lat_file  = dict_source["MetadataDevice"]["Latitude"] 
                    long_file = dict_source["MetadataDevice"]["Longitude"]

                if type_files_in_dir == "images" or type_files_in_dir == "videos":
                    dict_source["MetadataFiles"][filename]["GPSLatitude"]  = lat_file
                    dict_source["MetadataFiles"][filename]["GPSLongitude"] = long_file
                else:
                    if type_files_in_dir == "audios":
                        dict_source["MetadataFiles"][filename]["Latitude"]  = lat_file
                        dict_source["MetadataFiles"][filename]["Longitude"] = long_file
                logger.info("Writing lat long of centroid for MetadataFiles")
                dict_source["MetadataFiles"][filename]["CentroidCumulusLatitude"]  = lat_centroid_cumulus
                dict_source["MetadataFiles"][filename]["CentroidCumulusLongitude"] = long_centroid_cumulus
                file_with_metadata_dst = os.path.join(input_directory,
                                                      input_directory_name) + \
                                                      "_simex_metadata_files_and_device_" + \
                                                      datetime.date.today().strftime(date_format) + \
                                                      ".json"
                pathlib.Path(file_with_metadata_dst).unlink(missing_ok=True) #remove in case it exists
                with open(file_with_metadata_dst, 'w') as dst:
                    json.dump(dict_source, dst)

    except Exception as e:
        logger.info(e)
        logger.info("unsuccessful query %s or error when moving files to standard dir" % operation_sgqlc)
