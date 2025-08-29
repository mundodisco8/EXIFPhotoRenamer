"""Mass Renamer
This Module will grab all the image/video files in a folder and rename them.
The images are sorted by dat and time of capture, and are renamed with the following pattern

`YYYY-MM-DD string XX.ext`

Where YYYY-MM-DD is the date of capture, string is a... string, and XX is an increasing counter
for images captured in the same day.

This module generates a JSON file with metadata for the images and videos on a folder.
The metadata will be used later for a mass rename process. This process takes a while (~1s per
image) so you might want to skip it on folders with lots of files.

The JSON data will be exported to a file named `data_file_sorted.json`. This file will
contain one key for each image/video file in a folder and it's subfolders, and the value
of that key will be a dictionary with the date and time of creation as strings and a boolean
flag indicating if a sidecar file is present for that particular file (as it would have to be
renamed too).

Example of a JSON key
```
{
    [...]
    "folder/2 May 2018 - 3 of 185.heic": {
        "date": "2018:05:02",
        "time": "11:50:20",
        "hasSidecar": false
    },
    [...]
}

Functions:
---------
    findCreationTime: for a file with EXIF data, finds the best candidate for
    the creation date and time.
    hasSidecar: looks for sidecar files with the same name as the image (for some reason
    Photos on Mac exported them with an extra `O` in the name, before the extension ¯\\_(ツ)_/¯)
    generateSortedJSON: loops through a folder and generates a JSON file with the images/videos
    on it, and the metadata needed in the renaming process
"""

from datetime import datetime, timedelta
from subprocess import Popen, PIPE, run
from json import load, JSONDecodeError
from pathlib import Path
from re import compile, search
from typing import Dict, List
from enum import IntEnum
from logging import getLogger

from exiftool import ExifToolHelper

module_logger = getLogger(__name__)

# Format strings for partsing datetimes in aware and naive formats (with and without UTC
# offset). Annoyingly, to parse a datetime to string and have a semicolon in the offset,
# you use the %:z token, but that token doesn't work when parsing strings to datetime!
offsetAwareFormatParsing = "%Y:%m:%d %H:%M:%S%z"
offsetAwareFormatStringing = "%Y:%m:%d %H:%M:%S%:z"
offsetNaiveFormat = "%Y:%m:%d %H:%M:%S"

# # TODO: Software source: Apps leave a tag in Software, but so do iPhone photos.
# # Software Instagram or Layout from Instagram
# # Software Adobe Photoshop
# # ...

# # A definition of the dictionary which is used as value for our JSON, containing the
# # metadata for each file to be processed later.


# class metadataDict(TypedDict):
#     date: str        # date in format YYYY-MM-DD
#     time: str        # time in format HH:MM:SS
#     hasSidecar: bool  # indicates if this file has a sidecar
#     dateless: bool   # indicates that this file didn't have a good exif tag for date of creation
#     screenshot: bool  # Indicates that the file is a screenshot
#     # indicates if the file comes from a "camera" or from an app (Whatsapp, etc...)
#     hasManufacturer: bool


# # Filename for the JSON file to use
# jsonFileName: str = "data_file_sorted.json"
# Filename to use the metadata obtained from the ExifTool batch processing
etJSON: Path = Path("etJSON.json")
objectFile: Path = Path("MediaFileList.txt")

# # define this to search for "0000:00:00 00:00:00", an empty date and time
# emptyDate: str = "0000:00:00 00:00:00"

# # The List of tags to extract with exiftool
# # HACK: sometimes, the filemodifydate tag can help, but it can also be quite harmful, so
# # by default I won't add it to the list of tags
# tagsToExtract: List[str] = ["-UserComment", "-CreateDate", "-DateTimeOriginal",
#                             "-MediaCreareDate", "-Make", "-Model", "-Software", "-filemodifydate"]


# ####
# ##
# # Compiled Regexes
# ##

# # To check for time offsets: +/-HH:MM
# offsetRegEx = compile(r'[\+\-][0-9]{2}\:[0-9]{2}')

# Searches for "YYYY:MM:DD HH:MM:SS" with an optional "[+/-]XX:XX" or "Z"
dateTimeRegEx = compile(r"(\d{4}\:\d{2}\:\d{2}\s\d{2}\:\d{2}\:\d{2}([\+\-]\d{2}\:\d{2}|[Z])?)")

# # List of known video extensions. Add them in lowercase
# videoExtensions: List[str] = [".mov", ".mp4", ".m4v"]
# # List of known photo extensions. Add them in lowercase
# photoExtensions: List[str] = [".heic", ".jpg",
#                               ".jpeg", ".png", ".gif", ".tif", ".tiff"]
# List of known "don't process" files
dontProcessExtensions: List[str] = [".aae", ".ds_store"]

####
# Misc stuff, helpers, etc
####


class TZ_AWARENESS(IntEnum):
    NAIVE = 1
    AWARE = 2
    Z_AWARE = 3  # Date is TZ Aware, but uses Z suffix


# def getListOfFiles(path: Path) -> List[Path]:
#     """
#     Returns a list of files in a folder, excluding those whose extension is listed in the
#     dontProcessExtensions list above

#     Args:
#         path: a Path to the folder

#     Returns:
#         a list of Paths to all the files in the folder (excluding some extensions)
#     """
#     if not path.is_dir():
#         module_logger.error(f"'{path}' is not a folder!")
#         exit()
#     return [file for file in path.rglob("*") if file.is_file() and file.suffix not in dontProcessExtensions]


# def orderDictByDate(jsonDict: OrderedDict[str, metadataDict]) -> OrderedDict[str, metadataDict]:
#     """
#     Reorders a dictionary, first based on date and then based on time

#     Args:
#         jsonDict, a dict with a metadataDict as value, to be sorted

#     Returns:
#         an ordered Dict, with keys sorted by date and then time of creation
#     """

#     retVal: OrderedDict[str, metadataDict] = OrderedDict()
#     # Use a try catch bad dictionaries without the required keys
#     try:
#         retVal = OrderedDict(
#             sorted(jsonDict.items(), key=lambda item: (item[1]["date"], item[1]["time"])))
#     except KeyError:
#         module_logger.error( "Couldn't find 'date' and/or 'time' trying to sort a dict!")
#         exit()
#     return retVal


# def stripOffset(date: str) -> Tuple[str, str]:
#     """
#     Strips the offset bit of a date (from HH:MM:SS[+-]OH:OM to HH:MM:SS). If the date has
#     no offset, returns the date as it was

#     Args:
#         date: a string with a date (formatted HH:MM:SS) with or without an offset ([+-]OH:OM)

#     Returns:
#         strippedDate: the date without the offset
#         offset: the offset, if there was one, or empty.
#     """

#     # Strip the offset, if it's included in the date
#     m = offsetRegEx.search(date)
#     strippedDate: str = ""
#     offset: str = ""
#     if date and m:
#         # Time includes offset, so remove offset from date
#         strippedDate = offsetRegEx.split(date)[0]
#         offset = m[0]
#         # module_logger.debug(f"Stripped offset from date! {date} + {offset}")
#     else:
#         # module_logger.error("NO OFFSET")
#         # if no match from the regex, return the date/time as it is
#         strippedDate = date
#     return strippedDate, offset


# def executeExifTool(exifToolInstance: ExifTool, arguments: List[str]) -> bool:
#     output = exifToolInstance.execute(*arguments)
#     if "weren't updated due to errors" in str(output):
#         module_logger.error(f"{output}")
#         return False
#     return True

####
# Creation date finder - findCreationTime
####


# NOTE: Tested
def getTZAwareness(dateTimeStr: str) -> TZ_AWARENESS | None:
    # If time is timezone-naive, add UTC offset
    appendOffsetFlag: bool = True
    try:
        datetime.strptime(dateTimeStr, offsetNaiveFormat)
        return TZ_AWARENESS.NAIVE
    except ValueError:
        # not Naive, try aware
        try:
            datetime.strptime(dateTimeStr, offsetAwareFormatParsing)
            if dateTimeStr[-1] == "Z":
                return TZ_AWARENESS.Z_AWARE
            else:
                return TZ_AWARENESS.AWARE
        except ValueError:
            # Is this a date string?
            return None


# NOTE: Tested
def getTimeOffset(exifToolData: Dict[str, str], exifTag: str):
    """
    Adds time offset to strings containing "naive" dateTime objects. If the dictionary
    doesn't have offset info, the date is assumed to be UTC ("+00:00").
    Eg: adds "+00:00" to "YYYY:MM:DD HH:MM:SS" if the timezone was UTC

    Args:
        exifToolData: a dict containing a collection of EXIF tags
        exifTag: the key of the dictionary containing the date in string format

    Returns:
        a string containing a date with time offset.
    """
    dateString_: str = exifToolData[exifTag]

    # Check if object is naive
    try:
        datetime.strptime(dateString_, offsetNaiveFormat)
    except ValueError:
        print(f"String does not contain a date in the correct format -> '{dateString_}'")
        raise ValueError
    # try to get offset from tags
    offset_: str = "+00:00"
    if exifTag == "EXIF:CreateDate":
        if "EXIF:OffsetTimeDigitized" in exifToolData.keys():
            offset_ = exifToolData["EXIF:OffsetTimeDigitized"]
    elif exifTag == "EXIF:DateTimeOriginal":
        if "EXIF:OffsetTimeOriginal" in exifToolData.keys():
            offset_ = exifToolData["EXIF:OffsetTimeOriginal"]
    # Otherwise, no tags associated, offset is still +00:00
    # Special case, sometimes offset is Z, for Zulu -> UTC
    if offset_ == "Z":
        offset_ = "+00:00"
    return dateString_ + offset_


# These are the tags that I'm capturing with EXIFTool about creation time
dateTagsToCheck: List[str] = [
    "EXIF:DateTimeOriginal",
    "QuickTime:DateTimeOriginal",
    "XMP:DateTimeOriginal",
    "EXIF:CreateDate",
    "QuickTime:CreateDate",
    "PNG:CreateDate",
    "XMP:CreateDate",
    "QuickTime: CreationDate",
]
# NOTE: Keeping this one for later, and thinking about capturing Track* in videos: is there a video that has no
# CreateDate but has track? unlikely
videoTagsToCheck: List[str] = ["File:FileModifyDate"]


# NOTE: Tested
def findCreationTime(exifToolData: Dict[str, str]) -> str | None:
    """
    Returns the Creation Time and Date (in the local time) of creation of a file
    with EXIF data and the time offset respect UTC, extracted from the metadata returned by
    ExifTool for that file, which is a list of attributes.
    If the file has no sources for a valid UTC offset, we will consider the dates UTC.

    From https://photo.stackexchange.com/questions/69959/
        DateTimeOriginal: best tag to use
        CreateDate: should be the same as DateTimeOriginal. Could be different if you are "scanning" a paper photo,
        where CreateDate is the date of the Scan, and DateTimeOriginal should be the date the photo was taken.


    Args:
        exifToolData: a dict with the metadata to extract, as provided by
            ExifTool
        tagsToChec (list of str): a list of tags to check for dates. They vary depending
            on the type of content

    Returns:
        date: a string with the creation date, time and offset of a file or an empty
        string if there is no valid date tags in the dictionary.
    """

    datesFound: List[datetime] = []
    # Gather all the date data from the tags we are interested in checking
    for tag in dateTagsToCheck:
        # if tag exists, grab store value in datesFound
        if tag in exifToolData:
            dateString_: str = exifToolData[tag]
            # We either have a datetime object that is aware, or we have a naive with an
            # offset. Turn back into string and store
            try:
                datetime.strptime(dateString_, offsetNaiveFormat)
                # if dateString is "naive" see if we can get the offset
                dateString_ = getTimeOffset(exifToolData, tag)
            except:
                pass
            # Else, the dateString is "aware"
            # Store the date as datetime object, so we can sort it later
            datesFound.append(datetime.strptime(dateString_, offsetAwareFormatParsing))

    if datesFound:
        datesFound = sorted(datesFound)
        # Pick the first element of the sorted array (sorted from oldest to newest) to get
        # the oldest date
        oldestDate_ = datesFound[0]
        # But there might be a couple of dates that are the "same", with and without offset
        # The sorting algo favours UTC over dates with offset, so that means that we can
        # potentially loose it on those scenarios. Loop the array for other dates equivalent
        # the picked one, but with an offset
        for date in datesFound:
            if date == oldestDate_:
                # if dates are still the same, prefer the one with the delta
                if date.utcoffset() != timedelta(0):
                    oldestDate_ = date
                    # and stop searching. If there are more equivalent dates with other
                    # deltas... well that's a mess anyway. Let's stop this madness here.
                    break
            else:
                # if dates are different, we can stop searching
                break
        return oldestDate_.strftime("%Y:%m:%d %H:%M:%S%:z")
    # Else, no dates were found, return None, this element is "dateless", we will
    # have to rely in file system data (unreliable) or infer by name, based on neighboring
    # dated elements.
    return None


####
# File Source finders: determines the source of different types of files
####


# NOTE: Tested
def isScreenShot(exifToolData: Dict[str, str]) -> bool:
    """
    Checks if a file is a screenshot.
    On iOS, screenshots are tagged as such by adding a "UserComment" tag with the contents
    "screenshot" on it.

    Args:
        ExifToolData: a dict with the metadata for the file, as provided by ExifTool

    Returns:
        true if it is, false otherwise
    """
    # screenshots
    isScreenShotFlag: bool = False
    # If there's any key with partial match with "UserComment", the list comprehension
    # will not be empty
    userCommentKeys = [key for key in exifToolData.keys() if "usercomment" in key.lower()]
    # Check for each key, while the flag is false, if the UserComment is "screenshot"
    if userCommentKeys != []:
        for key in userCommentKeys:
            # stop searching if one key with screenshot is found
            if isScreenShotFlag == False and "screenshot" in exifToolData[key].lower():
                isScreenShotFlag = True
    # Else, no "comment" keys, return false

    return isScreenShotFlag


# NOTE: Tested
def isInstaOrFace(exifToolData: Dict[str, str]) -> bool:
    """
    Checks if a file is from Instagram / Facebook Apps.
    We check for partial matches of "instagram" or "facebook" in the EXIF:Software tag

    Args:
        ExifToolData: a dict with the metadata for the file, as provided by ExifTool

    Returns:
        true if it is, false otherwise
    """

    isInstaFlag: bool = False
    # If there's any key with partial match with "Software", the list comprehension
    # will not be empty
    softwareKeys = [key for key in exifToolData.keys() if "software" in key.lower()]
    # Check for each key, while the flag is false, if the UserComment contains "facebook"
    # or "instagram"
    if softwareKeys != []:
        for key in softwareKeys:
            # stop stearching if one key with screenshot is found
            if (
                isInstaFlag == False
                and "facebook" in exifToolData[key].lower()
                or "instagram" in exifToolData[key].lower()
            ):
                isInstaFlag = True

    return isInstaFlag


# NOTE: Tested
def isPicsArt(exifToolData: Dict[str, str]) -> bool:
    """
    Checks if a file is from PicsArt Apps.
    The EXIF:Software tag is set to "PicsArt"

    Args:
        ExifToolData: a dict with the metadata for the file, as provided by ExifTool

    Returns:
        true if it is, false otherwise
    """

    if "EXIF:Software" in exifToolData.keys() and exifToolData["EXIF:Software"] == "PicsArt":
        return True

    return False


# NOTE: Tested
def getFileSource(exifToolData: Dict[str, str]) -> str:
    """
    Returns the "source" of the file.
    Normally, it's the model of the camera ("iPhone 8", "Pixel 7", "XT-30", ...), but
    if the file has no make and model, we can use it to tag 'WhatsApp' photos or screenshots

    Args:
        ExifToolData: a Dict with the tag data, as generated by ExifTool

    Returns:
        A string to use as the name pattern for the file, with the source of the file (a
        camera model, an app name, screenshot, ...)
    """
    # Checks for make and model
    hasManufacturerFlag: bool = False

    hasMake = any("make" in key.lower() for key in exifToolData.keys())
    hasModel = any("model" in key.lower() for key in exifToolData.keys())

    # NOTE: about make and model
    # So far, I found 3 "make" tags: EXIF (photos), QuickTime (Apple video) and XMP
    # All the files that had XMP:Make, had EXIF:Make too, and they were the same value.
    # No files had Quicktime and XMP make tags.
    # The same is true about "model"

    if hasModel:
        # if it has model, use it as naming pattern.
        modelKeyList: List[str] = [key for key in exifToolData if "model" in key.lower()]
        # If more than one "model" tags are present, check that all report the same model
        if len(modelKeyList) > 1:
            if len(set([exifToolData[model] for model in modelKeyList])) != 1:
                raise Exception(
                    f"Multiple mismatching 'model' tags found in {exifToolData['SourceFile']}: {modelKeyList}"
                )
        # Grab the first model tag and return it's value
        modelKey = modelKeyList[0]
        return exifToolData[modelKey]
    elif hasMake:
        # if we don't have a model, but we have a make, use that. Same algo as above
        makeKeyList: List[str] = [key for key in exifToolData if "make" in key.lower()]
        # If more than one "make" tags are present, check that all report the same model
        if len(makeKeyList) > 1:
            if len(set([exifToolData[make] for make in makeKeyList])) != 1:
                raise Exception(
                    f"Multiple mismatching 'make' tags found in {exifToolData['SourceFile']}: {makeKeyList}"
                )
        # Grab the first model tag and return it's value
        makeKey = makeKeyList[0]
        return exifToolData[makeKey]
    else:
        # No make or model: file doesn't come from a camera, or the metadata was lost
        # Let's do some checks, to try to find the source, otherwise apply the "WhatsApp" tag
        if isScreenShot(exifToolData):
            return "Screenshot"
        elif isInstaOrFace(exifToolData):
            return "Insta_FaceBook"
        elif isPicsArt(exifToolData):
            return "PicsArt"
        # Check if it has an "app" as source
        else:
            return "WhatsApp"


def getSidecar(fileName: Path) -> Path | None:
    """Finds if a file has a sidecar associated with it
    For an image with name pattern `name.ext`, sidecars have the name pattern of `name.aae`
    or `nameO.aae`

    Args:
        fileName (Path): a Path to the file to check for sidecars

    Returns:
        The path to a sidecar, if exists, or None if not found
    """

    sidecar = fileName.parent / Path(fileName.stem).with_suffix(".aae")
    # for some reason, sometimes they append an 'O' to the name of the file?
    sidecarO = fileName.parent / Path(fileName.stem + "O").with_suffix(".aae")
    if sidecar.is_file():
        # module_logger.info(, f"sidecar for {fileName.stem}{fileName.suffix} found")
        return sidecar
    elif sidecarO.is_file():
        # module_logger.info(, f"sidecar for {fileName.stem}{fileName.suffix} found (with O suffix)")
        return sidecarO
    else:
        # module_logger.error(f"No sidecar for {fileName} / {fileName.stem}{fileName.suffix}")
        return None


# def doExifToolBatchProcessing(path: Path) -> None:
#     """
#     Processes a folder with ExifTool and gathers a list of tags for each file

#     Args:
#         path: a Path to the folder to process

#     """
#     files = getListOfFiles(path)
#     files = natsorted(files)
#     module_logger.info(, f"Found {len(files)} files")

#     # # Do batch processing with ExifTool: extract all the relevant tags for our files
#     start = time()
#     with ExifTool() as et:
#         # Data to extract:
#         # CreateDate: time the file was written to flash (there's also DateTimeOriginal, which is when the shutter was actuated!)
#         # MediaCreateDate: alternative for video files to CreateDate, if that's missing
#         # Make and Model: used to determine if the doc comes from a "camera" or an "app"
#         etData: List = et.execute_json(*tagsToExtract, str(path), "-r")
#     module_logger.info( f"Processed {len(files)} files in {time() - start:0.02f}s")

#     with open(etJSON, "w+") as writeFile:
#         dump(etData, writeFile)

# # Used to keep track of directory changes when traversing the FS
# oldDirectory: Path = Path()


# def massRenamer(jsonData: OrderedDict[str, metadataDict], photosDir: Path, isDryRun: bool = False, namePattern: str = "iPhone", selectionSubfolder: str = "") -> None:
#     """
#     Performs a mass rename based on the contents of a JSON file generated on a previous
#     step.

#     Args:
#         fileName: the path to the folder containing the JSON file with the files to rename
#         isDryRun: a debugging bool flag. If true, no rename ops are performed, just printed
#         on screen. False by default (perform rename by default)
#         namePatter: the string pattern to use to rename the files, "iPhone" if none passed.
#     """
#     # Date Histogram:
#     # Find how many entries share the same date. We want to know this to figure out
#     # how many zeroes the file index will have, so they are naturally sorted in the
#     # file explorer
#     dateHistogram = Counter(jsonData[key]['date'] for key in jsonData)

#     # Counter used to name the files, starts on 1, and increases for each file with the
#     # same capture date
#     # One for no
#     counter: int = 1
#     # String used to find when the date changes
#     prevDateStr: str = ""
#     for key in jsonData:
#         dateStr = jsonData[key]['date']
#         numberOfZeroes = len(str(dateHistogram[dateStr]))
#         # module_logger.info(f"{dateStr} has {dateHistogram[dateStr]} files")
#         # Check the current date, and if it's the same as the previous one, increase counter. Otherwise, reset it to 1
#         if dateStr == prevDateStr:
#             counter += 1
#         else:
#             counter = 1

#         # This is the list of files we are going to hanlde:
#         # Store the current file and the name the file will have after the rename, as Paths
#         currentFile = Path(key)
#         renamedFile = photosDir / selectionSubfolder / \
#             f"{dateStr.replace(':', '-')} - {namePattern} {counter:>0{numberOfZeroes}}{currentFile.suffix}"

#         if not renamedFile.parent.is_dir():
#             module_logger.debug(f"Creating {renamedFile.parent} folder")
#             renamedFile.parent.mkdir(parents=True, exist_ok=True)
#         # Check if the file has a sidecar. They have the same filename than their parent file
#         # with .aae extension, but sometimes they have an 'O' at the end of the name ¯\_(ツ)_/¯
#         sidecarPath: Path = Path()
#         renamedSidecarPath = renamedFile.with_suffix(".aae")

#         # Print the name of the folder, if it's the first file in this folder we process
#         global oldDirectory
#         if currentFile.parent != oldDirectory:
#             module_logger.info(f"In {currentFile.parent}:")
#         oldDirectory = currentFile.parent  # and remember current folder for next run

#         if jsonData[key]['hasSidecar']:
#             # Sometimes the sidecar has O at the end of the filename (most of the times), sometimes
#             # it doesn't. If the file with the O doesn't exist, try without it
#             sidecarPath = currentFile.parent / f"{currentFile.stem}O.aae"
#             if not sidecarPath.is_file():
#                 # module_logger.error("NO SIDECAR FOUND WITH O.aae, trying without O")
#                 sidecarPath = currentFile.parent / f"{currentFile.stem}.aae"
#                 if not sidecarPath.is_file():
#                     module_logger.error( "NO SIDECAR FOUND WITH OR WITHOUT O.aae PATTERN")
#                 else:
#                     # module_logger.info(, "SIDECAR FOUND WITH O.aae pattern")
#                     pass  # leaving this in case I want to enable the debug log
#             else:
#                 # module_logger.info(, "SIDECAR FOUND WITH O.aae pattern")
#                 pass  # leaving this in case I want to enable the debug log

#         # Check if the file exists before doing anything on it. This is useful to skip files that
#         # have been processed in previous passes, without having to recreate the JSON file
#         # Print the folder name the first time we see a "new folder"
#         if isDryRun == False:
#             # It's time to rename the files...
#             if currentFile.is_file():
#                 # if file exists, rename (maybe was renamed on previous runs)
#                 currentFile.replace(renamedFile)
#             if sidecarPath.is_file():
#                 module_logger.info(, f"Trying with sidecar {sidecarPath.name} for file {renamedFile.name}")
#                 sidecarPath.replace(renamedSidecarPath)
#         else:
#             # If dry-run is used, only print name changes
#             print(
#                 lvl.OK + f"File Name: {currentFile.name}\t->\t" + lvl.WARNING + f"{renamedFile.name}")
#             if jsonData[key]['hasSidecar']:
#                 module_logger.error( f"\t And also rename sidecar {sidecarPath.name} to {renamedSidecarPath.name}")
#         prevDateStr = dateStr


# def showAllTags(fileName: Path) -> None:
#     """Shows all tags for a pased file"""
#     with ExifToolHelper() as eth:
#         fmetadata = eth.get_metadata(str(fileName))
#         module_logger.error(f"File is {fileName}")
#         for data in fmetadata:
#             for key, value in data.items():
#                 module_logger.info(, f"{key}\t{value}")
#             if "EXIF:DateTimeOriginal" in data:
#                 module_logger.debug( f"{data['SourceFile']}\t{data['EXIF:DateTimeOriginal']}")
#             elif "File:FileModifyDate" in data:
#                 module_logger.debug( f"{data['SourceFile']}\t{data['File:FileModifyDate']}")
#             else:
#                 module_logger.debug( f"{fileName} has no DateTimeOriginal tag")


# def printAllDates(file: Path) -> None:
#     with ExifTool() as et:
#         print(et.execute("-time:all", "-G1", "-a", "-s", str(file)))


# def test():
#     # # Grab all tags needed
#     # files = getListOfFiles(path)
#     # files = natsorted(files)
#     # module_logger.info(, f"Found {len(files)} files")
#     # # Do batch processing with ExifTool: extract all the relevant tags for our files
#     # start = time()
#     # with ExifTool() as et:
#     #     # Data to extract:
#     #     # CreateDate: time the file was written to flash (there's also DateTimeOriginal, which is when the shutter was actuated!)
#     #     # MediaCreateDate: alternative for video files to CreateDate, if that's missing
#     #     etData: List = et.execute_json("-XMP:UserComment", "-CreateDate", "-MediaCreareDate", str(path), "-r")
#     # module_logger.info(, f"Processed {len(files)} files in {time() - start:0.02f}s")
#     # JSON file exists, process it. Pass the dryRun flag

#     etData: List[OrderedDict] = []
#     with open(etJSON, "r") as readFile:
#         etData = load(readFile)

#     keyList: List[str] = []
#     makeList: List[str] = []
#     modelList: List[str] = []
#     softwareList: List[str] = []
#     for item in etData:
#         for key in item.keys():
#             if key not in keyList:
#                 keyList.append(key)
#             if "Make" in key and key not in makeList:
#                 makeList.append(key)
#             if "Model" in key and key not in modelList:
#                 modelList.append(key)
#             if "Software" in key and key not in softwareList:
#                 softwareList.append(key)

#     # print(keyList)
#     # print(makeList)
#     # print(modelList)
#     # print(softwareList)
#     usedSW: List[str] = []
#     for item in etData:
#         photoMake: str = ""
#         photoModel: str = ""
#         photoSoftware: str = ""
#         for make in makeList:
#             if photoMake == "" and make in item:
#                 photoMake = item[make]
#         for model in modelList:
#             if photoModel == "" and model in item:
#                 photoModel = item[model]
#         for software in softwareList:
#             if photoSoftware == "" and software in item:
#                 photoSoftware = item[software]
#                 if "adobe" in str(photoSoftware).lower():
#                     module_logger.debug(f"{item['SourceFile']}")
#                 if photoSoftware not in usedSW:
#                     usedSW.append(photoSoftware)

#         if photoMake != "" and photoMake != "Apple":
#             module_logger.info(f"{item['SourceFile']}: {photoMake} and {photoModel}")
#         # if photoSoftware != "" and p
#     usedSW = natsorted(usedSW)

#     # Date Histogram:
#     # Find how many entries share the same date. We want to know this to figure out
#     # how many zeroes the file index will have, so they are naturally sorted in the
#     # file explorer
#     dateHistogram: dict = Counter()
#     for software in softwareList:
#         dateHistogram.update(item[software] for item in etData if software in item)

#     dateHistogram = OrderedDict(sorted(dateHistogram.items(), key=lambda item:item[1]))

#     # for key in dateHistogram:
#     #     module_logger.info(, f"{key}\t -> \t{dateHistogram[key]}")


class MediaFile:
    """
    A class to represent any media file (video or photo)

    Instance Attributes:
    --------------------
    _fileName: Path
        filename of the media file
    _dateTime: str
        The date of creation: string with format YYYY:MM:DD HH:MM:SS+OO:OO(default: "")
    _hasSidecar: bool
        Flag to indicate if object has sidecar (default: False)
    _source: str
        Origin of the file: iPhone, WhatsApp, screenshot, camera... (default: "")

    Methods:
    --------
    """

    # Use slots, instead of a dict, for the attributes. This makes the attribs static,
    # but require less memory per object and has faster access
    __slots__ = "_fileName", "_dateTime", "_source", "_sidecar"

    # NOTE: Tested
    def __init__(self, fileName: Path, dateTime: str | None, source: str):
        """
        Attributes:
        -----------
        _fileName: Path
            filename of the media file
        _dateTime: str
            The date and time of creation: string with format 'YYYY:MM:DD hh:mm:ss', or
            None if it has not been determined yet..
        _source: str
            Origin of the file: iPhone, WhatsApp, screenshot, camera... (default: "")
        """
        self._fileName: Path = fileName

        if dateTime:
            self.setTime(dateTime)
        else:
            self._dateTime = None

        self._sidecar: Path | None = getSidecar(fileName)
        self._source: str = source

    @classmethod
    def fromExifTags(cls, etTagsDict: Dict[str, str]):
        # Get the filename for the object
        try:
            filename_: Path = Path(etTagsDict["SourceFile"])
        except KeyError:
            print(f"No SourceFile tag in the EXIF metadata! -> {etTagsDict}")
            raise
        # Try to find a date of creation, if available in the passed tags
        dateTime_: str | None = findCreationTime(etTagsDict)
        # Find the source
        try:
            source_: str = getFileSource(etTagsDict)
        except KeyError:
            print("Error")
            raise

        return cls(fileName=filename_, dateTime=dateTime_, source=source_)

    # NOTE: Tested
    def __repr__(self):
        """
        Returns a string with the representation of the object: this string could be used to init an instance
        Example: MediaFile(fileName='Name', dateTime='1234-12-12 11-22-33+03:00', source="Apple iPhone 8")
        """
        return (
            f"{type(self).__name__}"
            f'(fileName=Path("{self._fileName}"), '
            f'dateTime="{self._dateTime}", '
            f'source="{self._source}")'
        )

    def getTime(self):
        return self._dateTime

    # NOTE: Tested
    def setTime(self, newTime: str) -> None:
        # Validate time
        if not dateTimeRegEx.match(newTime):
            module_logger.error(f"Invalid date string, '{newTime}', try again")
            return
        # Get awareness of date
        if getTZAwareness(newTime) == TZ_AWARENESS.NAIVE:
            newTime += "+00:00"
        # If offset is Z, replace it with a "+00:00", it does nothing if it's not
        newTime = newTime.replace("Z", "+00:00")
        self._dateTime = newTime

    def getFileName(self):
        return self._fileName


###
# FILE MANIPULATION - Read from and write to file
###


def getFilesInFolder(inputFolder: Path) -> int:
    """Gets the number of files that ExifTool can process in the folder RECUSIVELY

    Args:
        inputFolder (Path): folder to inspect

    Returns:
        int: total number of files that ExifTool can process
    """
    numFiles: int = 0
    cmdFind: list[str | Path] = ["exiftool", "-listdir", "-r", inputFolder]
    p = run(cmdFind, stdout=PIPE, stderr=PIPE, shell=True, text=True)
    result = search("([0-9]*) image files read", p.stdout)
    if result:
        numFiles = int(result.group(1))
    return numFiles


# NOTE: Tested
def loadMediaFileListFromFile(inputFile: Path) -> List[MediaFile]:
    """Loads and returns a list of MediaFile objects stored in a file passed as input

    Args:
        inputFile (Path): a file containing a list of MediaFile objects as text

    Returns:
        List[MediaFile]: a list of MediaFile objects
    """
    mediaFileList: List[MediaFile] = []
    try:
        with open(inputFile, "r") as readFile:
            mediaFileData: str = readFile.read()
    except FileNotFoundError:
        module_logger.error(f"{inputFile} could not be found")
        raise

    try:
        mediaFileList = eval(mediaFileData)
    except SyntaxError:
        module_logger.error(f"{inputFile} contents could not be eval()'ed")
        raise

    if not isinstance(mediaFileList[0], MediaFile):
        raise TypeError(f"{inputFile} didn't contain a list of MediaFile")

    return mediaFileList


# NOTE: Tested
def storeMediaFileList(outputFile: Path, listMediaFiles: List[MediaFile]) -> None:
    """
    Stores the list MediaFile objects passed as parameter in the file specified

    Args:
        outputFile (Path): name of the file to store the data to.
        listTags (List[MediaFile]): a list of MediaFile objects.
    """
    with open(outputFile, "w") as writeFile:
        writeFile.write(str(listMediaFiles))


# NOTE: Tested
def loadExifToolTagsFromFile(inputFile: Path) -> List[Dict[str, str]]:
    """
    Reads the output file from the EXIFTool batch processing (a collection of EXIF
    tags).

    The input JSON file contains tags from EXIFTool.
    NOTE: be careful with paths!

    Args:
        inputFile (Path): path to the file containing the output of ExifTool

    Returns:
        List[Dict[str, str]]: a list of dictionaries with the tags for each file.
    """
    etData: List[Dict[str, str]] = []
    try:
        with open(inputFile, "r") as readFile:
            # Check the file has JSON data on it
            try:
                etData = load(readFile)
            except JSONDecodeError:
                module_logger.error("File doesn't contain JSON data")
                raise
    except FileNotFoundError:
        module_logger.error(f"{inputFile} could not be found")
        raise

    return etData


# NOTE: Tested
def storeExifToolTags(outputFile: Path, listTags: List[Dict[str, str]]) -> None:
    """
    Stores the list tags passed as parameter in the file specified

    Args:
        outputFile (Path): name of the file to store the data to.
        listTags (List[Dict[str,str]]): a list of dictionaries, containing the EXIF tags
        as key-value pairs, from EXIFTool
    """

    with open(outputFile, "w") as writeFile:
        writeFile.write(str(listTags))


####
# The important stuff! This are the functions that provide the functionality of this
# module.
####


# NOTE: Tested
def generateSortedMediaFileList(etData: List[Dict[str, str]]) -> List[MediaFile]:
    """
    Creates a list of MediaFile objects from a list of dictionaries with tags comming from
    EXIFTool.

    Args:
        etData (List[Dict[str, str]): a list of dictionaries. Each dictionary is a collection of tags
        obtained from EXIFTool

    Returns:
        List[MediaFile]: a list of MediaFile objects, ready to be processed
    """
    mediaFileList: List[MediaFile] = []

    for entry in etData:
        # The batch processor of ExifTool processes all files in folder, so remove
        # known bad extensions. Get the filename and check its extension
        fileName: Path = Path(entry["SourceFile"])
        # We have to check 'suffix' for files with name.extension ('example.aae'), and name for files with name starting with . ('.ds_store')
        if (fileName.suffix.lower() not in dontProcessExtensions) and (
            fileName.name.lower() not in dontProcessExtensions
        ):
            mediaFileList.append(MediaFile.fromExifTags(entry))

    # Sorts the list based on the filename. This will help to infer dates based on
    # "neighbours" with date.
    mediaFileList = sorted(mediaFileList, key=lambda x: x.getFileName())
    return mediaFileList


####
# Creation date fixers
####


# NOTE: Tested
def inferDateFromNeighbours(datelessMFIdx: int, mediaFileList: List[MediaFile]) -> str | None:
    """infers the date of creation of a dateless item in a list of MediaFile. It infers a date based on the file's neighbours.

    Args:
        datelessMFIdx (int): index of the item in mediaFileList that we want to get a new date for
        mediaFileList (List[MediaFile]): a list of MediaFile objects (so we can infer the date from the neighbours)

    Returns:
        str | None: the selected new date of capture for the item, or None if the file was skipped
    """

    # The list has to be ordered by filename, otherwise the times we infer might not be
    # very relevant
    # We start with a list of Photo objects, and the item without a date.
    # Get the index of the item to date (or get it as paramenter?)
    # Check the previous item in the list of instances, and the element following it
    # If a date is found, add that date plus a minute, for example
    # If first or last item is reached, stop searching in that direction
    oneMinute = timedelta(minutes=1)
    addTime: bool = True
    datedObjectIdx: int = 0
    i: int = 1
    while datelessMFIdx >= i:
        if mediaFileList[datelessMFIdx - i].getTime() is not None:
            datedObjectIdx = datelessMFIdx - i
            # convert time to dateTime to easily add one minute to it
            break
        i += 1

    if datedObjectIdx == 0:
        # No "previous" file had a date, start to look "forward"
        i = 1
        while datelessMFIdx + i < len(mediaFileList):
            if mediaFileList[datelessMFIdx + i].getTime() is not None:
                datedObjectIdx = datelessMFIdx + i
                addTime = False
                break
            i += 1

    if datedObjectIdx != 0:
        if addTime:
            newTime = datetime.strptime(mediaFileList[datedObjectIdx].getTime(), offsetAwareFormatParsing) + (
                oneMinute * i
            )  # type: ignore # Complains about the possibility of dateTime being None
        else:
            newTime = datetime.strptime(mediaFileList[datedObjectIdx].getTime(), offsetAwareFormatParsing) - (
                oneMinute * i
            )  # type: ignore # Complains about the possibility of dateTime being None
        return newTime.strftime(offsetAwareFormatStringing)
    # else, Could not find a single dated item!
    return None


# Given a dateless file, print all the date tags the file has (from exiftool). This will include filesystem ones
# Infer date from neighbours
# Print all the gathered dates
# Let user select and save new date
# Add option to skip
# Return new element with date (or same one if skipped)


def _getInput() -> str:
    """
    Using a wrapper in input, so we can mock it, as it seems it can't be patched
    """
    return input()


# NOTE: Tested
def fixDateInteractive(datelessMFIdx: int, mediaFileList: List[MediaFile]) -> str | None:
    """Fixes the date of a dateless item in a list of MediaFile. It presents a number of options from all the date
    tags from the file, plus it infers a date based on the file's neighbours, and allows you to pick the best choice

    Args:
        datelessMFIdx (int): index of the item in mediaFileList that we want to get a new date for
        mediaFileList (List[MediaFile]): a list of MediaFile objects (so we can infer the date from the neighbours)

    Returns:
        str | None: the selected new date of capture for the item, or None if the file was skipped
    """

    # Get all the "date" tags present in the file
    fileName = mediaFileList[datelessMFIdx].getFileName()
    datesList: list[str] = []
    with ExifToolHelper() as et:
        datesList = et.execute("-time:all", "-G1", "-a", "-s", str(fileName)).splitlines()
    # Add the inferred date from its neighbours to the list
    inferredDate = inferDateFromNeighbours(datelessMFIdx, mediaFileList)
    if inferredDate:
        datesList.append(f"[Inferred Date] {inferredDate}")

    module_logger.info("Found these date tags:")
    # Print all the options available
    for idx, date_ in enumerate(datesList):
        idx += 1
        module_logger.info(f"{idx}) {date_}")

    # Read selected date from console. If the input is not an int, return 0 and skip file
    module_logger.info(
        f"Do you want to pick one of these dates [1-{len(datesList)}]? (0 to skip this file, -1 if you are bored and want to save and quit)",
    )
    try:
        chosenIdx = int(_getInput())
    except:
        chosenIdx = 0

    # Parse the input
    newDate: str | None = None
    try:
        if chosenIdx > 0 and chosenIdx <= len(datesList):
            # One of the given dates from ExifTool
            matchObj = dateTimeRegEx.search(datesList[chosenIdx - 1])  # list is 0-indexed
            if matchObj:
                newDate = matchObj.group()
                # TODO: WHAT TO DO IF THIS DATE IS NOT TZ AWARE, BUT WE COULD GET THAT INFO FROM OTHER TAGS?
                return newDate
            else:
                module_logger.error(f"Couldn't find a date in {datesList[chosenIdx - 1]}")
        elif chosenIdx < 0:
            storeMediaFileList(objectFile, mediaFileList)
            exit(0)
        else:
            # skip the file from being tagged
            return None
    except IndexError:
        # if the input was not an int, skip this file
        return None


### STEP 2 Process Data and Extract


def generateMediaFileList(EXIFTagFile: Path) -> None:
    # Being quite explicit:
    # 1) read exif tags from file -> generate list of dicts
    exifDicts: List[Dict[str, str]] = loadExifToolTagsFromFile(EXIFTagFile)
    # 2) Use list of dicts -> generate list of MediaFile
    mediaList: List[MediaFile] = generateSortedMediaFileList(exifDicts)
    print(mediaList)
    # 3) Store MediaFile list on disk
    storeMediaFileList(objectFile, mediaList)
    # 4) Find Dateless, try to correct them by hand
    dateless = [instance for instance in mediaList if instance.getTime() == None]
    print(dateless)
    print(f"Found {len(dateless)} {'instance' if (len(dateless) == 1) else 'instances'} without date")
    for item in dateless:
        # find item in mediaList
        idx = mediaList.index(item)
        newDate = fixDateInteractive(idx, mediaList)
        if newDate:
            mediaList[idx].setTime(newDate)

    storeMediaFileList(objectFile, mediaList)

    return
