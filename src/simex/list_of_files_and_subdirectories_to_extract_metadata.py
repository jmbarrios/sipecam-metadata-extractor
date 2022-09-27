import argparse
import datetime
from pathlib import Path

from simex import SUFFIXES_SIPECAM

def arguments_parse():
    help = """
Given a directory with SiPeCaM files, produce list of files whose metadata
will be extracted and list of directories where data will be copied
(traditional server).
--------------
Example usage:
--------------

list_of_files_and_subdirectories_to_extract_metadata --input_directory /input_dir

"""


    parser = argparse.ArgumentParser(description=help,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--input_directory",
                        required=True,
                        default=None,
                        help="Directory with data: audio, image and video")
    args = parser.parse_args()
    return args

def main():
    args = arguments_parse()
    input_directory = Path(args.input_directory)
    shared_volume = Path("/shared_volume")
    shared_volume.mkdir(parents=True, exist_ok=True)
    date_str = datetime.date.today().strftime("%d-%m-%Y")
    sipecam_subdirectories = ( shared_volume /
            f"sipecam_subdirectories_{date_str}.txt" )
    sipecam_files_to_extract_metadata = ( shared_volume /
            f"sipecam_files_to_extract_metadata_from_{date_str}.txt" )

    list_of_files = [f.resolve() for f in input_directory.glob('**/*')
                     if f.suffix in SUFFIXES_SIPECAM]
    list_of_subdirectories = { f.parent for f in list_of_files }

    with sipecam_files_to_extract_metadata.open(mode='w+') as f:
        f.writelines([f'{str(i)}\n' for i in list_of_files])

    with sipecam_subdirectories.open(mode='w+') as f:
        f.writelines([f'{str(i)}\n' for i in list_of_subdirectories])

