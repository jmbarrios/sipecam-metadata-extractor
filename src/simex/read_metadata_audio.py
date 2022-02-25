import re
from datetime import datetime
from datetime import date

import exiftool


ID_REGEX       = re.compile(r'AudioMoth ([0-9A-Z]{16})')
DATE_REGEX     = re.compile(r'((\d{2}:\d{2}:\d{2}) (\d{2}\/\d{2}\/\d{4}) \((UTC((-|\+)(\d+))?)\))')
GAIN_REGEX     = re.compile(r'gain setting (\d)')
GAIN_REGEX_ALT = re.compile(r'at (\w*) gain')
BATTERY_REGEX  = re.compile(r'battery state was (\d.\dV)')
ONLY_DATE_REGEX = re.compile(r'(\d{2}\/\d{2}\/\d{4})')
ONLY_TIME_REGEX = re.compile(r'(\d{2}:\d{2}:\d{2})')

TAGS = ["File:FileSize",
        "RIFF:Encoding",
        "RIFF:NumChannels",
        "RIFF:SampleRate",
        "RIFF:AvgBytesPerSec",
        "RIFF:BitsPerSample",
        "RIFF:Comment",
        "Composite:Duration"]  

def get_am_battery_state(comment):
    match = BATTERY_REGEX.search(comment)
    return match.group(1)

def get_am_gain(comment):
    match = GAIN_REGEX.search(comment)
    if match is None:
        match = GAIN_REGEX_ALT.search(comment)
    return match.group(1)

def transform_time_zone(tz,
                        offset_direction_with_offset,
                        offset_direction,
                        offset):
    if len(offset) != 4:
        offset = '{:02d}00'.format(int(offset))
    return tz.replace(offset_direction_with_offset,
                      offset_direction + offset) #returns UTC<offset direction><2digits including offset>00: example: UTC-0600

def get_date_with_timezone(comment):
    match = DATE_REGEX.search(comment)
    timezone = match.group

    raw = match.group(1)
    time = match.group(2)
    date = match.group(3)
    tz = match.group(4)
    offset_direction_with_offset = match.group(5)
    offset_direction = match.group(6)
    offset = match.group(7)

    try:
        new_tz = transform_time_zone(tz,
                                     offset_direction_with_offset,
                                     offset_direction,
                                     offset)
        date_with_timezone = raw.replace(tz, new_tz)
    except Exception:
        pass
    return date_with_timezone #example: 21:20:00 28/07/2021 (UTC-0600)

def get_am_id(comment):
    match = ID_REGEX.search(comment)
    return match.group(1)

def get_timezone_name(date_with_timezone):
    if "(UTC)" in date_with_timezone:
        datetime_format = '%H:%M:%S %d/%m/%Y (%Z)'
        timezone_name = "UTC"
    else:
        datetime_format = '%H:%M:%S %d/%m/%Y (%Z%z)'
        datetime_file = datetime.strptime(date_with_timezone,
                                          datetime_format)
        timezone_name = datetime_file.tzinfo.tzname(datetime_file)
    return timezone_name

def get_date(comment):
    match_date = ONLY_DATE_REGEX.search(comment)
    date_of_file = match_date.group(1)
    format_string_data = "%d/%m/%Y"
    return date.isoformat(datetime.strptime(date_of_file,
                                            format_string_data)) #convert to Y-m-d format

def get_comment(filename):
    with exiftool.ExifTool() as et:
        return et.get_tag("Comment", filename)

def get_metadata_of_device(filename):
    comment_metadata = get_comment(filename)
    gain = get_am_gain(comment_metadata)
    date_with_timezone = get_date_with_timezone(comment_metadata)
    timezone = get_timezone_name(date_with_timezone)
    serial_number = get_am_id(comment_metadata)
    return {"Gain"    : gain,
            "Timezone": timezone,
            "SerialNumber": serial_number
            }
def get_metadata_of_file(filename):
    comment_metadata = get_comment(filename)
    battery = get_am_battery_state(comment_metadata)
    date_with_timezone = get_date_with_timezone(comment_metadata)
    #see: https://github.com/sylikc/pyexiftool/issues/21
    with exiftool.ExifTool(common_args=["-G"]) as et:
        exiftool_metadata = et.get_tags(TAGS, filename)
    dict_metadata_of_file = {"Battery"  : battery,
                             "Datetime" : date_with_timezone
                             }
    for t in TAGS:
        dict_metadata_of_file[t] = exiftool_metadata[t]
    return dict_metadata_of_file

def extract_serial_number(filename):
    comment_metadata = get_comment(filename)
    return get_am_id(comment_metadata)

def extract_date(filename):
    comment_metadata = get_comment(filename)
    return get_date(comment_metadata)#example: 2021-07-28
