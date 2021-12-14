import glob
import os
import re
import argparse
from argparse import RawTextHelpFormatter

from . import read_metadata_image, read_metadata_audio, \
              read_metadata_video
from . import get_logger_for_writing_logs_to_file

def arguments_parse():
    help = """
Extract metadata of file, fill fields of File model in
Zendro and copy file to directory of server. Write logs for each
step.

--------------
Example usage:
--------------

extract_metadata_and_ingest_it --input_file /dir/filename.(WAV|JPG|AVI)

"""


    parser = argparse.ArgumentParser(description=help,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--input_file",
                        required=True,
                        default=None,
                        help="File that will be processed")
    parser.add_argument("--node",
                        type=str,
                        help="Node nomenclature",
                        required=False)
    parser.add_argument("--cumulus",
                        type=str,
                        help="Cumulus name",
                        required=False)
    args = parser.parse_args()
    return args

def main():
    args = arguments_parse()
    input_file = args.input_file
    node_nomenclature = args.node
    cumulus_name = args.cumulus
    logger = get_logger_for_writing_logs_to_file(input_file,
                                                 "temp_logs_simex_extract_metadata_and_ingest")
    logger.info("extraction of metadata and ingestion of %s" % input_file)
    wav_extensions = "WAV|wav"
    jpg_extensions = "JPG|jpg"
    avi_extensions = "AVI|avi"

    if re.search(wav_extensions, input_file):
        logger.info("Read metadata of WAV")
        dict_metadata_audio = read_metadata_audio.get_metadata(input_file)
        logger.info(dict_metadata_audio)
        type_of_file = "WAV"
    if re.search(avi_extensions, input_file):
        logger.info("Read metadata of AVI")
        dict_metadata_video = read_metadata_video.get_metadata(input_file)
        logger.info(dict_metadata_video)
        type_of_file = "AVI"
    if re.search(jpg_extensions, input_file):
        logger.info("Read metadata of JPG")
        dict_metadata_image = read_metadata_image.get_metadata(input_file)
        logger.info(dict_metadata_image)
        type_of_file = "JPG"

    if node_nomenclature:
        logger.info("Node nomenclature was given from cli")
        if cumulus_name:
            logger.info("Cumulus name was given from cli")
    else:
        logger.info("Getting node nomenclature and cumulus name from zendro")
        #node_nomenclature, cumulus_name = get_node_and_cumulus_name_from_zendro()
        node_nomenclature, cumulus_name = "1_3_1_28", "3"
    #date_of_device_deployment = get_date_of_device_deployment_from_kobo()
    date_of_device_deployment = "2021-10-01"
    output_directory = os.path.join(cumulus_name, node_nomenclature,
                                    date_of_device_deployment,
                                    type_of_file)
    logger.info("Copying file to %s" % output_directory)



