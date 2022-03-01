import exiftool

TAGS_1_FOR_FILE = ["EXIF:Make",
                   "EXIF:Model",
                   "MakerNotes:SerialNumber",
                   "File:FileSize",
                   "File:ExifByteOrder",
                   "File:ImageWidth",
                   "File:ImageHeight",
                   "File:EncodingProcess",
                   "File:BitsPerSample",
                   "File:ColorComponents",
                   "File:YCbCrSubSampling",
                   "EXIF:XResolution",
                   "EXIF:YResolution",
                   "EXIF:ResolutionUnit",
                   "EXIF:YCbCrPositioning",
                   "EXIF:ExposureTime",
                   "EXIF:ISO",
                   "EXIF:TimeZoneOffset",
                   "EXIF:ComponentsConfiguration",
                   "EXIF:ColorSpace",
                   "EXIF:GPSLatitudeRef",
                   "EXIF:GPSLongitudeRef",
                   "MakerNotes:AmbientTemperature",
                   "MakerNotes:Contrast",
                   "MakerNotes:Brightness",
                   "MakerNotes:Sharpness",
                   "MakerNotes:Saturation",
                   "MakerNotes:Flash",
                   "MakerNotes:AmbientInfrared",
                   "MakerNotes:AmbientLight",
                   "MakerNotes:MotionSensitivity",
                   "MakerNotes:BatteryVoltage",
                   "MakerNotes:BatteryVoltageAvg",
                   ]

TAGS_2_FOR_FILE = ["Composite:GPSLatitude",
                   "Composite:GPSLongitude",
                   "Composite:Megapixels"
                   ]


TAGS_FOR_DEVICE = ["EXIF:Make",
                   "EXIF:Model",
                   "MakerNotes:SerialNumber"
                  ]

def get_metadata_of_device(filename):
    with exiftool.ExifTool() as et:
        exiftool_metadata = et.get_tags(TAGS_FOR_DEVICE, filename)
    dict_metadata_of_device = {}
    for t in TAGS_FOR_DEVICE:
        if t == "MakerNotes:SerialNumber":
            dict_metadata_of_device["SerialNumber"] = exiftool_metadata[t]
        else:
            dict_metadata_of_device[t] = exiftool_metadata[t]
    return dict_metadata_of_device

def get_metadata_of_file(filename):
    with exiftool.ExifTool(common_args=["-G"]) as et:
        exiftool_metadata_1 = et.get_tags(TAGS_1_FOR_FILE, filename)
    with exiftool.ExifTool() as et:
        exiftool_metadata_2 = et.get_tags(TAGS_2_FOR_FILE, filename)
    dict_metadata_of_file = {}
    for t in TAGS_1_FOR_FILE:
        if t == "MakerNotes:SerialNumber":
            dict_metadata_of_file["SerialNumber"] = exiftool_metadata_1[t]
        else:
            dict_metadata_of_file[t] = exiftool_metadata_1[t]
    for t in TAGS_2_FOR_FILE:
        dict_metadata_of_file[t] = exiftool_metadata_2[t]
    return dict_metadata_of_file

def extract_date(filename):
    with exiftool.ExifTool() as et:
        datetimeoriginal = et.get_tag("DateTimeOriginal", filename)
        datetimeoriginal_splitted = datetimeoriginal.split(" ")
    return datetimeoriginal_splitted[0].replace(":","-") #example: 2021-07-28

def extract_serial_number(filename):
    with exiftool.ExifTool() as et:
        return et.get_tag("SerialNumber", filename)
