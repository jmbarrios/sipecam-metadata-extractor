import exiftool

from hachoir.parser import createParser
from hachoir.metadata import extractMetadata
from hachoir.core import config as HachoirConfig

#see: https://stackoverflow.com/questions/38832691/suppress-warnings-in-hachoir
HachoirConfig.quiet = True #to supress warnings when calling extractMetadata of hachoir


TAGS_1_FOR_FILE = ["File:FileSize",
                   "File:BMPVersion",
                   "File:ImageWidth",
                   "File:ImageHeight",
                   "File:Planes",
                   "File:ImageLength",
                   "File:PixelsPerMeterX",
                   "File:PixelsPerMeterY",
                   "File:NumColors",
                   "File:NumImportantColors",
                   "RIFF:FrameRate",
                   "RIFF:FrameCount",
                   "RIFF:StreamCount",
                   "RIFF:AudioSampleCount",
                   "RIFF:Encoding",
                   "RIFF:NumChannels",
                   "RIFF:AvgBytesPerSec",
                   "RIFF:BitsPerSample",
                   "Composite:Duration"
                    ]

TAGS_2_FOR_FILE = ["RIFF:MaxDataRate",
                   "Composite:Megapixels"
                  ]

TAGS_FOR_DEVICE = ["RIFF:StreamName"]

def metadata_hachoir(filename):
    parser = createParser(filename)
    metadata = extractMetadata(parser)
    return metadata

def get_metadata_of_device(filename):
    with exiftool.ExifTool() as et:
        exiftool_metadata = et.get_tags(TAGS_FOR_DEVICE, filename)
    dict_metadata_of_device = {}
    for t in TAGS_FOR_DEVICE:
        dict_metadata_of_device[t] = exiftool_metadata[t]
    return dict_metadata_of_device

def get_metadata_of_file(filename):
    with exiftool.ExifTool(common_args=["-G"]) as et:
        exiftool_metadata_1 = et.get_tags(TAGS_1_FOR_FILE, filename)
    with exiftool.ExifTool() as et:
        exiftool_metadata_2 = et.get_tags(TAGS_2_FOR_FILE, filename)
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

    for t in TAGS_1_FOR_FILE:
        dict_metadata_of_file[t] = exiftool_metadata_1[t]
    for t in TAGS_2_FOR_FILE:
        dict_metadata_of_file[t] = exiftool_metadata_2[t]

    return dict_metadata_of_file

def extract_date(filename):
    with exiftool.ExifTool() as et:
        datetimeoriginal = et.get_tag("DateTimeOriginal", filename)
        datetimeoriginal_splitted = datetimeoriginal.split(" ")
    return datetimeoriginal_splitted[0].replace(":","-") #example: 2021-07-28
