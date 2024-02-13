"""Script to rename files using exiftools"""
# Made so far
#   1. Get files in a folder
#   2. Get their metadata
#   3. If a value exists, print, or don't if it doesn't
import sys
from os import environ, chdir
from re import compile
from datetime import datetime
from pathlib import Path, PosixPath
from exiftool import ExifToolHelper
from typing import Dict
from json import JSONEncoder, dumps, dump
from support.support import lvl, debugPrint

def in_virtualenv():
    """Silly check for virtual environments"""
    return "VIRTUAL_ENV" in environ


def findCreationTime(file: Path):
    """Returns the Creation Time of a file in the local time"""

    date: str = ""
    dateUTC: str = ""
    time: str = ""
    offset: str = ""

    # Searches for "[+/-]XX:XX" where XX:XX is time in HH:MM
    offsetRegEx = compile(r'[\+\-][0-9]{2}\:[0-9]{2}')
    with ExifToolHelper() as et:

        # Scan the metadata of the file to find the best candidate for a "Creation Time"
        metadata = et.get_metadata(file)
        for d in metadata:
            # Start with the DatetimeOriginal, which normally is the best option
            if "EXIF:DateTimeOriginal" in d:
                date = d["EXIF:DateTimeOriginal"]
            # Mov videos use the QuickTime:CreationDate
            elif "QuickTime:CreationDate" in d:
                date = d["QuickTime:CreationDate"]
            # Another option seems to be File:FileModifyDate
            elif "File:FileModifyDate" in d:
                date = d["File:FileModifyDate"]
            # Find the Offset in the time, as it's normally UTC
            if "EXIF:OffsetTime" in d:
                debugPrint(
                    lvl.DEBUG, f"{d['SourceFile']}\t{d['EXIF:OffsetTime']}")
                offset = d['EXIF:OffsetTime']

        # Print the value that will be used as the date
        # The value can be in "YYYY:mm:DD HH:MM:SS" or "YYYY:mm:DD HH:MM:SS[+-]OO:OO"
        # where [+-]OO:OO is an offset from UTC. For example: [date] 15:42:23+01:00 means
        # the picture was taken at 15:42:23 local time, 14:42:23 UTC
        # Becase we want to sort based on local time, we will strip that info, if found
        if date:
            debugPrint(lvl.DEBUG, f"{file}\t{date}")
        else:
            debugPrint(lvl.WARNING, f"{file}\t{'No DateTimeOriginal'}")

        # Print offset if found
        if offset:
            debugPrint(lvl.DEBUG, f"Offset is {offset}")

        # Strip the offset, if it's included in the date
        m = offsetRegEx.search(date)
        if date and m:
            # Time includes offset, so remove offset from date
            date = offsetRegEx.split(date)[0]
            offset = m[0]
            debugPrint(lvl.ERROR, f"Stripped offset from date! {date} + {offset}")
        else:
            debugPrint(lvl.ERROR, "NO OFFSET")
        # Commenting as probably will be too verbosy otherwise
        # else:
            # debugPrint(lvl.DEBUG, "No OFFSET on File")
        # split
        date, time = date.split()
    return date, time, offset

def hasSidecar(fileName: Path)->bool:
    # Strip path in filename and ext
    # Complete path + filename + ext
    # debugPrint(lvl.OK, f"Full path {fileName}")
    # filename only
    # debugPrint(lvl.WARNING, f"Filename {fileName.stem}")
    # extension only
    # debugPrint(lvl.ERROR, f"Extension {fileName.suffix}")
    # Just the directory path of the file
    # debugPrint(lvl.OK, f"Parent {fileName.parent}")
    sidecar = (Path(fileName.parent) / Path(fileName.stem)).with_suffix(".aae")
    if sidecar.is_file():
        # debugPrint(lvl.OK, f"sidecar for {fileName} found")
        return True
    else:
        # debugPrint(lvl.ERROR, f"No sidecar for {fileName}")
        return False



if not in_virtualenv():
    print("Not in VENV!")
    sys.exit()

# Path to Files -> TODO:will have to become an argument
# photosDir = Path( r"/media/joel/Backup/Fotos Mac Organizar/2016 - duplicates")
# Path With Sidecars
photosDir = Path(r"/media/joel/Backup/Fotos Mac Organizar/2018 - duplicates/2–6 May 2018")
# photosDir = Path(r"/media/joel/Backup/Fotos Mac Organizar/2018 - duplicates/")
# chdir(photosDir)
# files = list(Path().rglob('*'))
# List comprehension: every file in photosDir, recursively, if the file is "a file" and it's not .DS_Store
files = [file for file in photosDir.rglob("*") if file.is_file() and (file.stem != ".DS_Store")]
sidecars = list(Path().rglob('*.aae'))
if sidecars:
    debugPrint(lvl.WARNING, f"There are {len(sidecars)} sidecars")
    for sidecar in sidecars:
        debugPrint(lvl.WARNING, f"\t{sidecar}")
else:
    debugPrint(lvl.WARNING, "No Sidecars in folder")

debugPrint(lvl.OK, f"Found {len(files)} files")

testPath = Path("/media/joel/Backup/Fotos Mac Organizar/2018 - duplicates/2\u20136 May 2018/2\u20136 May 2018 - 55 of 185.heic")

# Create a JSON String with the data needed for the renaming process
# Date, to get the filename pattern "YYYY-MM-DD"
# Time, to sort images/videos with the same date
# has Sidecar, if a sidecar file has to be renamed with the file
# {
#     "fileA": {
#         "date": "2016-05-28",
#         "time": "15:23:43",
#         "hasSidecar": True
#     },
#     "fileB": {
#         "date": "2016-05-26",
#         "time": "17:26:43",
#         "hasSidecar": False
#     }
#     [...]
# }

# Create the JSON structure. Use a dict for it
# A dict using filenames as keys and date of creation as value
# datesDict: Dict[Path, str] = dict()
jsonDict: Dict[Path, Dict] = dict()
for file in files:
    date, time, __unused = findCreationTime(file)
    hasSidecarFlag = hasSidecar(file)
    jsonDict[str(file)] = {"date": date, "time": time, "hasSidecar": hasSidecarFlag}

# This sorts the dict based on value
jsonDict = dict(sorted(jsonDict.items(), key=lambda item: (item[1]["date"], item[1]["time"])))
with open("data_file_sorted.json", "w+") as write_file:
    dump(jsonDict, write_file)

# fileComplete = files[9]
# with ExifToolHelper() as eth:
#     # for file in files:
#     #     metadata = eth.get_metadata(file)
#     #     for d in metadata:
#     #         if "EXIF:DateTimeOriginal" in d:
#     #             print("{}\t{}".format(d["SourceFile"],
#     #                                         d["EXIF:DateTimeOriginal"]))
#     #         else:
#     #             print("{} has no DateTimeOriginal tag".format(files[0]))
#     fmetadata = eth.get_metadata(fileComplete)
#     debugPrint(lvl.ERROR, f"File is {fileComplete}")
#     for data in fmetadata:
#         for key, value in data.items():
#             debugPrint(lvl.OK, f"{key}\t{value}")
#         if "EXIF:DateTimeOriginal" in data:
#             debugPrint(lvl.DEBUG, f"{data['SourceFile']}\t{data['EXIF:DateTimeOriginal']}")
#         elif "File:FileModifyDate" in data:
#             debugPrint(lvl.DEBUG, f"{data['SourceFile']}\t{data['File:FileModifyDate']}")
#         else:
#             debugPrint(
#                 lvl.DEBUG, f"{fileComplete} has no DateTimeOriginal tag")
# findCreationTime(files[0])