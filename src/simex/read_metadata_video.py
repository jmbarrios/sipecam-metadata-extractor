import exiftool

from hachoir.parser import createParser
from hachoir.metadata import extractMetadata
from hachoir.core import config as HachoirConfig

#see: https://stackoverflow.com/questions/38832691/suppress-warnings-in-hachoir
HachoirConfig.quiet = True #to supress warnings when calling extractMetadata of hachoir


TAGS_1_FOR_FILE = {"File:FileSize"          : "FileSize"          ,
                   "RIFF:DateTimeOriginal"  : "DateTimeOriginal"  ,
                   "File:BMPVersion"        : "BMPVersion"        ,
                   "File:ImageWidth"        : "ImageWidth"        ,
                   "File:ImageHeight"       : "ImageHeight"       ,
                   "File:Planes"            : "Planes"            ,
                   "File:ImageLength"       : "ImageLength"       ,
                   "File:PixelsPerMeterX"   : "PixelsPerMeterX"   ,
                   "File:PixelsPerMeterY"   : "PixelsPerMeterY"   ,
                   "File:NumColors"         : "NumColors"         ,
                   "File:NumImportantColors": "NumImportantColors",
                   "RIFF:FrameRate"         : "FrameRate"         ,
                   "RIFF:FrameCount"        : "FrameCount"        ,
                   "RIFF:StreamCount"       : "StreamCount"       ,
                   "RIFF:AudioSampleCount"  : "AudioSampleCount"  ,
                   "RIFF:Encoding"          : "Encoding"          ,
                   "RIFF:NumChannels"       : "NumChannels"       ,
                   "RIFF:AvgBytesPerSec"    : "AvgBytesPerSec"    ,
                   "RIFF:BitsPerSample"     : "BitsPerSample"     ,
                   "Composite:Duration"     : "Duration"
                   }

TAGS_2_FOR_FILE = {"RIFF:MaxDataRate"     : "MaxDataRate",
                   "Composite:Megapixels" : "Megapixels"
                  }

def metadata_hachoir(filename):
    parser = createParser(filename)
    metadata = extractMetadata(parser)
    return metadata

def get_metadata_of_file(filename):
    with exiftool.ExifTool(common_args=["-G"]) as et:
        exiftool_metadata_1 = et.get_tags(TAGS_1_FOR_FILE.keys(), filename)
    with exiftool.ExifTool() as et:
        exiftool_metadata_2 = et.get_tags(TAGS_2_FOR_FILE.keys(), filename)
    hachoir_metadata_dict  = metadata_hachoir(filename).exportDictionary()
    bit_rate               = hachoir_metadata_dict["Common"]["Bit rate"]
    endianness             = hachoir_metadata_dict["Common"]["Endianness"]
    video_bits_per_pixel   = hachoir_metadata_dict["Video stream"]["Bits/pixel"]
    video_compression      = hachoir_metadata_dict["Video stream"]["Compression"]
    audio_sample_rate      = hachoir_metadata_dict["Audio stream"]["Sample rate"]
    audio_compression_rate = hachoir_metadata_dict["Audio stream"]["Compression rate"]
    audio_compression      = hachoir_metadata_dict["Audio stream"]["Compression"]
    audio_bit_rate         = hachoir_metadata_dict["Audio stream"]["Bit rate"]
    dict_metadata_of_file = {}
    dict_metadata_of_file["BitRate"]              = bit_rate
    dict_metadata_of_file["Endianness"]           = endianness
    dict_metadata_of_file["VideoBitsPerPixel"]    = video_bits_per_pixel
    dict_metadata_of_file["VideoCompression"]     = video_compression
    dict_metadata_of_file["AudioSampleRate"]      = audio_sample_rate
    dict_metadata_of_file["AudioCompressionRate"] = audio_compression_rate
    dict_metadata_of_file["AudioCompression"]     = audio_compression
    dict_metadata_of_file["AudioBitRate"]         = audio_bit_rate

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
