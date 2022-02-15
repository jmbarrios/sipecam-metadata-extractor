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

def get_am_battery_state(comment):
    match = BATTERY_REGEX.search(comment)
    return match.group(1)

def get_am_gain(comment):
    match = GAIN_REGEX.search(comment)
    if match is None:
        match = GAIN_REGEX_ALT.search(comment)
    return match.group(1)

def get_am_datetime(comment):
    match = DATE_REGEX.search(comment)
    timezone = match.group

    raw = match.group(1)
    time = match.group(2)
    date = match.group(3)

    tz = match.group(4)

    try:
        offset_direction = match.group(6)
        offset = match.group(7)

        if len(offset) != 4:
            offset = '{:02d}00'.format(int(offset))

        new_tz = tz.replace(match.group(5), offset_direction + offset)
        raw = raw.replace(tz, new_tz)
        tz = new_tz
    except Exception:
        pass

    if "(UTC)" in raw:
        datetime_format = '%H:%M:%S %d/%m/%Y (%Z)'
    else:
        datetime_format = '%H:%M:%S %d/%m/%Y (%Z%z)'

    return {
        'raw': raw,
        'time': time,
        'date': date,
        'tz': tz,
        'datetime': datetime.strptime(raw, datetime_format),
        'format': datetime_format
    }

def get_am_id(comment):
    match = ID_REGEX.search(comment)
    return match.group(1)

def get_comment(filename):
    with exiftool.ExifTool() as et:
        return et.get_tag("Comment", filename)

def extract_serial_number(filename):
    comment_metadata = get_comment(filename)
    return get_am_id(comment_metadata)

def get_datetime(comment):
    match_date = ONLY_DATE_REGEX.search(comment)
    date_of_file = match_date.group(1)
    format_string_data = "%d/%m/%Y"
    return date.isoformat(datetime.strptime(date_of_file, 
                                            format_string_data)) #convert to Y-m-d format

def extract_datetime_original(filename):
    comment_metadata = get_comment(filename)
    return get_datetime(comment_metadata)    

def get_metadata(filename):
    dict_metadata = {}
    return dict_metadata
