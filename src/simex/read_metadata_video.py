
def get_metadata(filename):
    dict_metadata = {}
    return dict_metadata


def extract_datetime_original(filename):
    with exiftool.ExifTool() as et:
        return et.get_tag("DateTimeOriginal", filename) 