import PIL.ExifTags
from PIL import Image
import re

import exiftool


def get_metadata(filename):
    dict_metadata = {}
    return dict_metadata

def extract_date(filename):
    with exiftool.ExifTool() as et:
        datetimeoriginal = et.get_tag("DateTimeOriginal", filename)
        datetimeoriginal_splitted = datetimeoriginal.split(" ")
    return datetimeoriginal_splitted[0].replace(":","-") #example: 2021-07-28

def extract_serial_number(filename):
    with exiftool.ExifTool() as et:
        return et.get_tag("SerialNumber", filename)
    
def extract_gps_position(filename):
    with exiftool.ExifTool() as et:
        return et.get_tag("GPSPosition", filename)