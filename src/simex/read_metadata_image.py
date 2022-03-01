import exiftool

TAGS_1_FOR_FILE = {"EXIF:Make"                     : "Make"                   ,
                   "EXIF:Model"                    : "Model"                  ,
                   "EXIF:DateTimeOriginal"         : "DateTimeOriginal"       ,
                   "MakerNotes:SerialNumber"       : "SerialNumber"           ,
                   "File:FileSize"                 : "FileSize"               ,
                   "File:ExifByteOrder"            : "ExifByteOrder"          ,
                   "File:ImageWidth"               : "ImageWidth"             ,
                   "File:ImageHeight"              : "ImageHeight"            ,
                   "File:EncodingProcess"          : "EncodingProcess"        ,
                   "File:BitsPerSample"            : "BitsPerSample"          ,
                   "File:ColorComponents"          : "ColorComponents"        ,
                   "File:YCbCrSubSampling"         : "YCbCrSubSampling"       ,
                   "EXIF:XResolution"              : "XResolution"            ,
                   "EXIF:YResolution"              : "YResolution"            ,
                   "EXIF:ResolutionUnit"           : "ResolutionUnit"         ,
                   "EXIF:YCbCrPositioning"         : "YCbCrPositioning"       ,
                   "EXIF:ExposureTime"             : "ExposureTime"           ,
                   "EXIF:ISO"                      : "ISO"                    ,
                   "EXIF:TimeZoneOffset"           : "TimeZoneOffset"         ,
                   "EXIF:ComponentsConfiguration"  : "ComponentsConfiguration",
                   "EXIF:ColorSpace"               : "ColorSpace"             ,
                   "EXIF:GPSLatitudeRef"           : "GPSLatitudeRef"         ,
                   "EXIF:GPSLongitudeRef"          : "GPSLongitudeRef"        ,
                   "MakerNotes:AmbientTemperature" : "AmbientTemperature"     ,
                   "MakerNotes:Contrast"           : "Contrast"               ,
                   "MakerNotes:Brightness"         : "Brightness"             ,
                   "MakerNotes:Sharpness"          : "Sharpness"              ,
                   "MakerNotes:Saturation"         : "Saturation"             ,
                   "MakerNotes:Flash"              : "Flash"                  ,
                   "MakerNotes:AmbientInfrared"    : "AmbientInfrared"        ,
                   "MakerNotes:AmbientLight"       : "AmbientLight"           ,
                   "MakerNotes:MotionSensitivity"  : "MotionSensitivity"      ,
                   "MakerNotes:BatteryVoltage"     : "BatteryVoltage"         ,
                   "MakerNotes:BatteryVoltageAvg"  : "BatteryVoltageAvg"      ,
                  }

TAGS_2_FOR_FILE = {"Composite:GPSLatitude"  : "GPSLatitude" ,
                   "Composite:GPSLongitude" : "GPSLongitude",
                   "Composite:Megapixels"   : "Megapixels"
                  }


TAGS_FOR_DEVICE = {"EXIF:Make"               : "Make"        ,
                   "EXIF:Model"              : "Model"       ,
                   "MakerNotes:SerialNumber" : "SerialNumber"
                  }

def get_metadata_of_device(filename):
    with exiftool.ExifTool() as et:
        exiftool_metadata = et.get_tags(TAGS_FOR_DEVICE.keys(), filename)
    dict_metadata_of_device = {}
    for k,v in TAGS_FOR_DEVICE.items():
        dict_metadata_of_device[v] = exiftool_metadata[k]
    return dict_metadata_of_device

def get_metadata_of_file(filename):
    with exiftool.ExifTool(common_args=["-G"]) as et:
        exiftool_metadata_1 = et.get_tags(TAGS_1_FOR_FILE.keys(), filename)
    with exiftool.ExifTool() as et:
        exiftool_metadata_2 = et.get_tags(TAGS_2_FOR_FILE.keys(), filename)
    dict_metadata_of_file = {}
    for k,v in TAGS_1_FOR_FILE.items():
        dict_metadata_of_file[v] = exiftool_metadata_1[k]
    for k,v in TAGS_2_FOR_FILE.items():
        dict_metadata_of_file[v] = exiftool_metadata_2[k]
    return dict_metadata_of_file

def extract_date(filename):
    with exiftool.ExifTool() as et:
        datetimeoriginal = et.get_tag("DateTimeOriginal", filename)
        datetimeoriginal_splitted = datetimeoriginal.split(" ")
    return datetimeoriginal_splitted[0].replace(":","-") #example: 2021-07-28

def extract_serial_number(filename):
    with exiftool.ExifTool() as et:
        return et.get_tag("SerialNumber", filename)
