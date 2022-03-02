import os
import argparse
import json
import pathlib
import datetime
import shutil
import hashlib

from simex import get_logger_for_writing_logs_to_file
from simex.utils.zendro import query_for_copy_files_to_standard_directory, \
query_alternative_auxiliar_for_copy_files_to_standard_directory, \
query_alternative_for_copy_files_to_standard_directory
from simex.utils.directories_and_files import multiple_file_types
from simex import SUFFIXES_SIPECAM_AUDIO, SUFFIXES_SIPECAM_IMAGES, SUFFIXES_SIPECAM_VIDEO, \
SUFFIXES_SIPECAM

def md5_for_file(path, block_size=256*128):
    """
    Block size directly depends on the block size of your filesystem
    to avoid performances issues
    Here I have blocks of 4096 octets (Default NTFS)
    See:
    https://stackoverflow.com/questions/1131220/get-md5-hash-of-big-files-in-python
    """
    md5 = hashlib.md5()
    with open(path,'rb') as f:
        for chunk in iter(lambda: f.read(block_size), b''):
             md5.update(chunk)
    return md5.hexdigest()

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
                                                         "_simex_extract_serial_numbers_dates_and_metadata_of_files_and_device.json"

    with open(file_with_serial_number_and_dates, 'r') as f:
        dict_source = json.load(f)

    serial_number = dict_source["MetadataDevice"]["SerialNumber"]
    dict_source_dates = dict_source["FirstAndLastDate"]
    diff_dates = dict_source["DaysBetweenFirstAndLastDate"]

    logger.info("Dir %s has serial number %s" % (directory_with_file_of_serial_number_and_dates,
                                                 serial_number))

    tup_source_dates = tuple(dict_source_dates.items())

    filename_source_first_date,  first_date_str  = tup_source_dates[0]
    filename_source_second_date, second_date_str = tup_source_dates[1]

    logger.info("File %s has date %s" % (filename_source_first_date,
                                             first_date_str))
    logger.info("File %s has date %s" % (filename_source_second_date,
                                             second_date_str))

    logger.info("DaysBetweenFirstAndLastDate: %s" % diff_dates)

    filename_source_first_date_pathlib = pathlib.Path(filename_source_first_date)

    def modify_json_metadata_of_files():
        pass

    def modify_json_metadata_of_device(d_source,
                                       nom_node,
                                       cumulus_name,
                                       date_deploy):
        dict_output_metadatadevice                     = d_source["MetadataDevice"].copy()
        dict_output_metadatadevice["NomenclatureNode"] = nom_node
        dict_output_metadatadevice["CumulusName"]      = cumulus_name
        dict_output_metadatadevice["DateDeployment"]   = date_deploy
        return dict_output_metadatadevice

    def move_files_to_standard_dir_and_modify_json_metadata(src_dir,
                                                            dst_dir,
                                                            d_source,
                                                            d_output_metadatadevice,
                                                            type_files_in_dir):

        if type_files_in_dir == "audios":
            dir_pathlib = pathlib.Path(src_dir)
            dict_output_metadata_audios_files  = {}
            dict_output_metadata_audios_files["MetadataDevice"] = d_output_metadatadevice
            standard_dir_audios = os.path.join(dst_dir,
                                               type_files_in_dir,
                                               dir_pathlib.parent.name #audible or ultrasonico
                                               )
            standard_dir_audios_pathlib = pathlib.Path(standard_dir_audios)
            os.makedirs(standard_dir_audios, exist_ok=True)
            file_with_metadata_updated_audios = os.path.join(standard_dir_audios,
                                                             standard_dir_audios_pathlib.name + \
                                                             "_simex_metadata_files_and_device.json")
            write_dst_audios = open(file_with_metadata_updated_audios, "w+")
            json.dump(dict_output_metadata_audios_files, write_dst_audios)
            dict_output_metadata_audios_files["MetadataFiles"] = {}
        else:
            if type_files_in_dir == "images" or "videos":
                dict_output_metadata_images_files  = {}
                dict_output_metadata_videos_files  = {}
                dict_output_metadata_images_files["MetadataDevice"] = d_output_metadatadevice
                dict_output_metadata_videos_files["MetadataDevice"] = d_output_metadatadevice
                standard_dir_images = os.path.join(dst_dir,
                                                   "images")
                standard_dir_videos = os.path.join(dst_dir,
                                                   "videos")
                standard_dir_images_pathlib = pathlib.Path(standard_dir_images)
                standard_dir_videos_pathlib = pathlib.Path(standard_dir_videos)
                os.makedirs(standard_dir_images, exist_ok=True)
                os.makedirs(standard_dir_videos, exist_ok=True)
                file_with_metadata_updated_images = os.path.join(standard_dir_images,
                                                                 standard_dir_images_pathlib.name + \
                                                                 "_simex_metadata_files_and_device.json")
                file_with_metadata_updated_videos = os.path.join(standard_dir_videos,
                                                                 standard_dir_videos_pathlib.name + \
                                                                 "_simex_metadata_files_and_device.json")
                write_dst_images = open(file_with_metadata_updated_images, "w+")
                write_dst_videos = open(file_with_metadata_updated_videos, "w+")
                dict_output_metadata_images_files["MetadataFiles"] = {}
                dict_output_metadata_videos_files["MetadataFiles"] = {}

        iterator = multiple_file_types(src_dir,
                                       SUFFIXES_SIPECAM)
        for filename in iterator:
            f_pathlib = pathlib.Path(filename)
            f_pathlib_suffix = f_pathlib.suffix
            filename_md5 = "".join([md5_for_file(filename),#basename of filename
                                    f_pathlib_suffix])#with suffix

            if f_pathlib_suffix in SUFFIXES_SIPECAM_AUDIO:
                logger.info("File %s will be moved to: %s with name %s" % (filename, standard_dir_audios,
                                                                           filename_md5)
                           )
                dst_filename = os.path.join(standard_dir_audios, filename_md5)
                f_pathlib.rename(dst_filename) #move
                dict_output_metadata_audios_files["MetadataFiles"][dst_filename] = d_source["MetadataFiles"][filename]

            else:
                if f_pathlib_suffix in SUFFIXES_SIPECAM_IMAGES:
                    logger.info("File %s will be moved to: %s with name %s" % (filename, standard_dir_images,
                                                                               filename_md5)
                               )
                    dst_filename = os.path.join(standard_dir_images, filename_md5)
                    f_pathlib.rename(dst_filename)
                    dict_output_metadata_images_files["MetadataFiles"][dst_filename] = d_source["MetadataFiles"][filename]

                else:
                    if f_pathlib_suffix in SUFFIXES_SIPECAM_VIDEO:
                        logger.info("File %s will be moved to: %s with name %s" % (filename, standard_dir_videos,
                                                                                   filename_md5)
                                   )
                        dst_filename = os.path.join(standard_dir_videos, filename_md5)
                        f_pathlib.rename(dst_filename)
                        dict_output_metadata_videos_files["MetadataFiles"][dst_filename] = d_source["MetadataFiles"][filename]

        if type_files_in_dir == "audios":
            json.dump(dict_output_metadata_audios_files, write_dst_audios)
            write_dst_audios.close()
        else:
            if type_files_in_dir == "images" or "videos":
                json.dump(dict_output_metadata_images_files, write_dst_images)
                json.dump(dict_output_metadata_videos_files, write_dst_videos)
                write_dst_images.close()
                write_dst_videos.close()

    #make query assuming first_date_str is less than date of deployment of device
    if filename_source_first_date_pathlib.suffix in SUFFIXES_SIPECAM_AUDIO:
        type_files_in_dir = "audios"
        query_result, operation_sgqlc = query_for_copy_files_to_standard_directory(serial_number,
                                                                                   first_date_str,
                                                                                   second_date_str,
                                                                                   file_type="audio")
    else:
        if filename_source_first_date_pathlib.suffix in SUFFIXES_SIPECAM_IMAGES:
            type_files_in_dir = "images"
            query_result, operation_sgqlc = query_for_copy_files_to_standard_directory(serial_number,
                                                                                       first_date_str,
                                                                                       second_date_str,
                                                                                       file_type="image")
        else:
            if filename_source_first_date_pathlib.suffix in SUFFIXES_SIPECAM_VIDEO:
                type_files_in_dir = "videos"
                query_result, operation_sgqlc = query_for_copy_files_to_standard_directory(serial_number,
                                                                                           first_date_str,
                                                                                           second_date_str,
                                                                                           file_type="video")

    logger.info("Query to Zendro GQL: %s" % operation_sgqlc)

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
            logger.info("modifying dict MetadataDevice")
            dict_output_metadatadevice = modify_json_metadata_of_device(dict_source,
                                                                        nomenclature_node,
                                                                        cumulus_name,
                                                                        date_of_deployment)
            path_with_files_copied = os.path.join(path_for_standard_directory,
                                                  cumulus_name,
                                                  nomenclature_node,
                                                  serial_number,
                                                  date_of_deployment)
            logger.info("path where files will be copied: %s" % path_with_files_copied)
            move_files_to_standard_dir_and_modify_json_metadata(directory_with_file_of_serial_number_and_dates,
                                                                path_with_files_copied,
                                                                dict_source,
                                                                dict_output_metadatadevice,
                                                                type_files_in_dir)

            #write new dict for metadata device and files

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
                        if len(device_deploymentsFilter_list) == 1:
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
                            logger.info("modifying dict MetadataDevice")
                            dict_output_metadatadevice = modify_json_metadata_of_device(dict_source,
                                                                                        nomenclature_node,
                                                                                        cumulus_name,
                                                                                        date_of_deployment)
                            path_with_files_copied = os.path.join(path_for_standard_directory,
                                                                  cumulus_name,
                                                                  nomenclature_node,
                                                                  serial_number,
                                                                  date_of_deployment)
                            logger.info("path where files will be copied: %s" % path_with_files_copied)
                            move_files_to_standard_dir_and_modify_json_metadata(directory_with_file_of_serial_number_and_dates,
                                                                                path_with_files_copied,
                                                                                dict_source,
                                                                                dict_output_metadatadevice,
                                                                                type_files_in_dir)
                    except Exception as e:
                        logger.info(e)
                        logger.info("unsuccessful query %s or error when moving files to standard dir" % operation_sgqlc)
                except Exception as e:
                    logger.info(e)
                    logger.info("unsuccessful query %s or error when moving files to standard dir" % operation_sgqlc)
            else: #len of list is >1 then there's no unique date of deployment of device
                logger.info("There's no unique date of deployment and can not select one date to create standard directory")
    except Exception as e:
        logger.info(e)
        logger.info("unsuccessful query %s or error when moving files to standard dir" % operation_sgqlc)
