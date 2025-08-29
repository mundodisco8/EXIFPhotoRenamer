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

from fileinput import filename
from alive_progress import alive_bar
from exiftool import ExifTool
from collections import OrderedDict, Counter
from datetime import datetime, timedelta
from exiftool import ExifToolHelper
from json import dump, load
from natsort import natsorted
from pathlib import Path
from re import compile
from time import time
from typing import OrderedDict, Dict, Tuple, List, TypedDict, Match

import natsort
from ..support.support import lvl, debugPrint

# TODO: Software source: Apps leave a tag in Software, but so do iPhone photos.
# Software Instagram or Layout from Instagram
# Software Adobe Photoshop
# ...

# A definition of the dictionary which is used as value for our JSON, containing the
# metadata for each file to be processed later.


class metadataDict(TypedDict):
    date: str  # date in format YYYY-MM-DD
    time: str  # time in format HH:MM:SS
    hasSidecar: bool  # indicates if this file has a sidecar
    dateless: bool  # indicates that this file didn't have a good exif tag for date of creation
    screenshot: bool  # Indicates that the file is a screenshot
    # indicates if the file comes from a "camera" or from an app (Whatsapp, etc...)
    hasManufacturer: bool


# Filename for the JSON file to use
jsonFileName: str = "data_file_sorted.json"
# Filename to use the metadata obtained from the ExifTool batch processing
etJSON: str = "etJSON.json"

# define this to search for "0000:00:00 00:00:00", an empty date and time
emptyDate: str = "0000:00:00 00:00:00"

# The List of tags to extract with exiftool
# HACK: sometimes, the filemodifydate tag can help, but it can also be quite harmful, so
# by default I won't add it to the list of tags
tagsToExtract: List[str] = [
    "-UserComment",
    "-CreateDate",
    "-DateTimeOriginal",
    "-MediaCreareDate",
    "-Make",
    "-Model",
    "-Software",
    "-filemodifydate",
]

# In images, we will check these tags (and in this order) for a date of creation
photoTagsToCheck: List[str] = [
    "EXIF:CreateDate",
    "EXIF:DateTimeOriginal",
    "PNG:CreateDate",
    "XMP:CreateDate",
    "File:FileModifyDate",
]
# In videos, we check these others
videoTagsToCheck: List[str] = ["QuickTime:CreateDate", "QuickTime:MediaCreateDate", "File:FileModifyDate"]

####
##
# Compiled Regexes
##

# To check for time offsets: +/-HH:MM
offsetRegEx = compile(r"[\+\-][0-9]{2}\:[0-9]{2}")

# Searches for "YYYY:MM:DD HH:MM:SS" with an optional "[+/-]XX:XX"
dateTimeRegEx = compile(r"(\d{4}\:\d{2}\:\d{2}\s\d{2}\:\d{2}\:\d{2}([\+\-]\d{2}\:\d{2})?)")

# List of known video extensions. Add them in lowercase
videoExtensions: List[str] = [".mov", ".mp4", ".m4v"]
# List of known photo extensions. Add them in lowercase
photoExtensions: List[str] = [".heic", ".jpg", ".jpeg", ".png", ".gif", ".tif", ".tiff"]
# List of known "don't process" files
dontProcessExtensions: List[str] = [".aae", ".ds_store"]


# Misc stuff, helpers, etc
####


def getListOfFiles(path: Path) -> List[Path]:
    """
    Returns a list of files in a folder, excluding those whose extension is listed in the
    dontProcessExtensions list above

    Args:
        path: a Path to the folder

    Returns:
        a list of Paths to all the files in the folder (excluding some extensions)
    """
    if not path.is_dir():
        debugPrint(lvl.ERROR, f"'{path}' is not a folder!")
        exit()
    return [file for file in path.rglob("*") if file.is_file() and file.suffix not in dontProcessExtensions]


def orderDictByDate(jsonDict: OrderedDict[str, metadataDict]) -> OrderedDict[str, metadataDict]:
    """
    Reorders a dictionary, first based on date and then based on time

    Args:
        jsonDict, a dict with a metadataDict as value, to be sorted

    Returns:
        an ordered Dict, with keys sorted by date and then time of creation
    """

    retVal: OrderedDict[str, metadataDict] = OrderedDict()
    # Use a try catch bad dictionaries without the required keys
    try:
        retVal = OrderedDict(sorted(jsonDict.items(), key=lambda item: (item[1]["date"], item[1]["time"])))
    except KeyError:
        debugPrint(lvl.ERROR, "Couldn't find 'date' and/or 'time' trying to sort a dict!")
        exit()
    return retVal


def stripOffset(date: str) -> Tuple[str, str]:
    """
    Strips the offset bit of a date (from HH:MM:SS[+-]OH:OM to HH:MM:SS). If the date has
    no offset, returns the date as it was

    Args:
        date: a string with a date (formatted HH:MM:SS) with or without an offset ([+-]OH:OM)

    Returns:
        strippedDate: the date without the offset
        offset: the offset, if there was one, or empty.
    """

    # Strip the offset, if it's included in the date
    m = offsetRegEx.search(date)
    strippedDate: str = ""
    offset: str = ""
    if date and m:
        # Time includes offset, so remove offset from date
        strippedDate = offsetRegEx.split(date)[0]
        offset = m[0]
        # debugPrint(
        # lvl.DEBUG, f"Stripped offset from date! {date} + {offset}")
    else:
        # debugPrint(lvl.ERROR, "NO OFFSET")
        # if no match from the regex, return the date/time as it is
        strippedDate = date
    return strippedDate, offset


def executeExifTool(exifToolInstance: ExifTool, arguments: List[str]) -> bool:
    output = exifToolInstance.execute(*arguments)
    if "weren't updated due to errors" in str(output):
        debugPrint(lvl.ERROR, f"{output}")
        return False
    return True


####
# Creation date finders
####


def findCreationTime(file: Path, ExifToolData: Dict[str, str], tagsToCheck: List[str]) -> Tuple[str, bool]:
    """Returns the Creation Time and Date (in the local time) of creation of a file
    with EXIF data and the time offset respect UTC, extracted from the metadata returned by
    ExifTool for that file, which is a list of attributes

    Args:
        photoFile (Path): a Pathlib path to the photo file to check
        ExifToolData: a dict with the metadata to extract, as provided by
            ExifTool
        tagsToChec (list of str): a list of tags to check for dates. They vary depending
            on the type of content

    Returns:
        date: a string with the creation date, time and offset (optional) of a file, and
            "0000:00:00 00:00:00" if no good dates were found in the file
        isDatelessFlag: a bool indicating if a date could be found (saves a check outside)
            of the function
    """
    date_: str = emptyDate  # default to empty date
    isDatelessFlag: bool = False

    for tag in tagsToCheck:
        # if tag exists, grab it as new date
        if tag in ExifToolData:
            date_ = ExifToolData[tag]
        # if the grabbed date is not empty, break the loop
        if not (emptyDate in date_):
            break
        # Else, the date grabbed is empty (0000:00:00...), keep checking tags

    # The second parameter is the "dateless" flag, true if no tags with date have been found
    # or if the date found in the tags is "0000:00:00...". Instead of dealing with lots of
    # cases, we check if the value returned is the empty date.
    isDatelessFlag = emptyDate in date_

    return date_, isDatelessFlag


def inferDateFromFile(jsonData: OrderedDict[str, metadataDict], jsonKey: str, fileList: List[Path]) -> Tuple[str, str]:
    """
    Infers the date of creation of a file based on previous files.

    Checks "previous" (as ordered in the filesystem) files for dates, and assigns the date of the closest, previous file
    that has a date, incremented by 5s for each file in between them.
    It's not ideal, but it's better than leaving files without metadata without a date of creation

    Args:
        jsonData: and OrderedDict with the JSON data containing the creation dates of the files in the current folder
        jsonKey: the key for the jsonData ordered Dict (a file path, as a string) of the file to infer.
        fileList: a naturally ordered list of files (so we can check the "previous files")

    Returns:
        The inferred date of creation for the file.
    """
    # We will check "previous" files until we find one with a time
    # Convert the list of Paths to list of strings, to locate the key, extract its order
    # in the list, and loop in reverse until a key with date is found
    fileListStr = [str(file) for file in fileList]
    foundADate: bool = False
    i: int = 1
    debugPrint(lvl.INFO, f"Inferring date for {Path(jsonKey).name}")
    previousKey: str = ""
    newTime: datetime
    while foundADate == False:
        previousKey = fileListStr[fileListStr.index(jsonKey) - i]
        if jsonData[previousKey]["dateless"]:
            debugPrint(lvl.WARNING, f"{Path(previousKey).name} doens't have a date")
            i = i + 1
        else:
            # Found an entry with a date, set our undated file to that date, plus some
            # seconds.
            debugPrint(
                lvl.OK,
                f"Assign date and time {jsonData[previousKey]['date']} / {jsonData[previousKey]['time']} from {Path(previousKey).name}",
            )
            foundADate = True
            # remove offset from time, if it has it
            timeStr, offset_ = stripOffset(jsonData[previousKey]["time"])
            newTime: datetime = datetime.strptime(timeStr, "%H:%M:%S")
            newTime = newTime + timedelta(0, i * 5)
    return jsonData[previousKey]["date"], newTime.strftime("%H:%M:%S")


def inferDateInteractive(
    jsonData: OrderedDict[str, metadataDict], jsonKey: str, fileList: List[Path]
) -> Tuple[str, str]:
    # # Load the JSON metadata: dict with filename as str key and metadataDict as value
    # with open(jsonFile, "r") as readFile:
    #     jsonData = load(readFile)

    with ExifTool() as et:
        datesList: List = et.execute("-time:all", "-G1", "-a", "-s", jsonKey).splitlines()
        # print(datesList)
        debugPrint(lvl.INFO, "Found these date tags:")
        # Print the dates found in the file
        idx: int = 0
        for idx, date_ in enumerate(datesList):
            idx += 1
            debugPrint(lvl.INFO, f"{idx}) {date_}")
        # Add an entry to the list with the inferred date based on filename.
        idx += 1
        inferDate, inferTime = inferDateFromFile(jsonData, jsonKey, fileList)
        debugPrint(lvl.INFO, f"{idx}) Inferred from filename: \t\t: {inferDate} {inferTime}")
        debugPrint(
            lvl.OK,
            f"Do you want to pick one of these dates [1-{idx}]? (0 to skip this file, -1 if you are bored and want to save and quit)",
        )
        # Read selected date from console. If the input is not an int, return -1
        try:
            chosenIdx = int(input())
        except:
            chosenIdx = 0
        # Pick one of the dates passed, if the index exists, or infer date otherwise
        try:
            if chosenIdx > 0 and chosenIdx < idx:
                result = dateTimeRegEx.search(datesList[chosenIdx - 1])  # list is 0-indexed
                if result:
                    newDate, newTime = result[0].split()
            elif chosenIdx == idx:
                newDate, newTime = inferDate, inferTime
            elif chosenIdx < 0:
                # You are bored, save and exit
                jsonData = orderDictByDate(jsonData)
                with open(jsonFileName, "w+") as write_file:
                    dump(jsonData, write_file)
                exit(0)
            else:
                # skip the file from being tagged
                skipFileFlag = True
        except IndexError:
            # if the input was not an int, skip this file
            skipFileFlag = True

        if skipFileFlag:
            # skipped the file, return an empty date
            newDate, newTime = emptyDate.split()
        return newDate, newTime


####
# Creation date fixers
####


def fixDateWithInferred(jsonFile: Path, filesToFix: List[str], photosFolder: Path) -> None:
    jsonData: OrderedDict[str, metadataDict] = OrderedDict()
    filesInFolder: List[Path] = getListOfFiles(photosFolder)
    # Sorting the file lists, as all the work is based on the order of these files in the hard drive
    filesInFolder = natsorted(filesInFolder)
    pathsToFix = (photosFolder / file for file in filesToFix)
    pathsToFix = natsorted(pathsToFix)

    # Load the JSON metadata: dict with filename as str key and metadataDict as value
    with open(jsonFile, "r") as readFile:
        jsonData = load(readFile)

    # DICT COMPREHENSION: just the dateless entries. Notice that we only use them to find the keys that are dateless
    # but we always store the results on jsonData, which contains both dateless and dated elements!
    # datelessItems = {key: value for (
    #     key, value) in jsonData.items() if jsonData[key]["dateless"] == True}

    # SHOW PROGRESS
    totalNumFiles: int = len(pathsToFix)

    # For each file that has the atribute dateless, either:
    # 1) get all the dates present in the file, print them, and ask which one to use.
    # 2) infer the date from the previous file, using the filename to decide the order
    # And then proceed to overwrite the JSON metadata and the file tags with the new date
    # Finally, we replace the metadata in the file with the newly found data, so we can
    # proceed to rename
    with ExifTool() as et:
        # We loop through datelessItems, but edit jsonData
        changesDict: dict[str, str] = dict()
        # Build changesDict, a dict with a date for each file, and print in screen. We will ask if we are happy
        # with the changes before applying them
        for filesDone, file_ in enumerate(pathsToFix):
            # The key for the JSON file is the path to the file to fix as a string
            key = str(file_)
            newDate: str = ""
            skipFileFlag: bool = False
            inferDate, inferTime = inferDateForDateless(jsonData, key, filesInFolder)
            debugPrint(lvl.OK, f"chosen {inferDate} {inferTime}")
            jsonData[key]["date"] = inferDate
            jsonData[key]["time"] = inferTime
            jsonData[key]["dateless"] = False
            # Write the inferred date as a tag. Probably not the most efficient way, but
            # I don't want to overcomplicate things.
            # The value of the tag to write, concatenating newDate and newTime
            tagValue: str = inferDate + " " + inferTime
            # The tag to use depends on whether it's a video or a photo:
            changesDict[key] = tagValue
        # Ask if we are happy with the changes propossed
        debugPrint(lvl.WARNING, "Are you happy with these dates? (y/n)")
        response = input()
        if response != "y":
            return  # nothing to do
        # Else, apply the changes
        with alive_bar(totalNumFiles) as bar:
            for key in changesDict:
                bar()
                if (file_.suffix).lower() in (photoExtensions + videoExtensions):
                    # Replace all time tags THAT EXIST (don't create new ones) with newDate
                    if not executeExifTool(
                        et, ["-ee", "-wm", "w", f"-time:all={changesDict[key]}", "-overwrite_original", key]
                    ):
                        debugPrint(lvl.ERROR, f"Error overwriting date tags on {Path(key).name}")
                    # If there is no CreateDate tag, create one and apply the value
                    if not executeExifTool(et, [f"-CreateDate={changesDict[key]}", "-overwrite_original", key]):
                        debugPrint(lvl.ERROR, f"Error overwriting date tags on {Path(key).name}")
                else:
                    debugPrint(lvl.ERROR, f"Unhandled case for {Path(key).name}")
    # All files must have dates now. Reorder dictionary with the new changes, and store in
    # the JSON file
    jsonData = orderDictByDate(jsonData)
    with open(jsonFileName, "w+") as write_file:
        dump(jsonData, write_file)


####
# File finders: return list of files based certain criteria
####


def hasManufacturer(fileName: Path, ExifToolData: Dict) -> bool:
    """
    Checks if the file has a "make" and "model" tag

    Args:
        fileName: a Path object to the file to check
        ExifToolData: a Dict with the tag data, as generated by ExifTool

    Returns:
        True if it has both a "make" and "model" tag, false otherwise
    """
    # Checks for make and model
    hasManufacturerFlag: bool = False

    hasMake = any("make" in key.lower() for key in ExifToolData.keys())
    hasModel = any("model" in key.lower() for key in ExifToolData.keys())

    if hasMake and hasModel:
        hasManufacturerFlag = True
    elif (hasMake and not hasModel) or (not hasMake and hasModel):
        debugPrint(lvl.WARNING, f"{fileName.name} only has Make OR Model")
    else:
        # do nothing
        pass

    # We didn't find the correct tag
    return hasManufacturerFlag


def isScreenShot(fileName: Path, ExifToolData: Dict) -> bool:
    """
    Checks if a file is a screenshot.
    On iOS, screenshots are tagged as such by adding a "UserComment" tag with the contents
    "screenshot" on it.

    Args:
        fileName, a file to check if it's a screenshot
        ExifToolData: a dict with the metadata for the file, as provided by
        ExifTool

    Returns:
        true if it is, false otherwise
    """
    # screenshots
    isScreenShotFlag: bool = False
    if "XMP:UserComment" in ExifToolData:
        if ExifToolData["XMP:UserComment"].lower() == "screenshot":
            isScreenShotFlag = True
        else:
            debugPrint(lvl.WARNING, f"UserComment in {fileName.name} is {ExifToolData['XMP:UserComment']}")

    # We didn't find the correct tag
    return isScreenShotFlag


def hasSidecar(fileName: Path) -> bool:
    """Finds if a file has a sidecar associated with it
    For an image with name pattern `name.ext`, sidecars have the name pattern of:
    `nameO.aae`

    Args:
        fileName (Path): a Path to the file to check for sidecars

    Returns:
        True if there's a sidecar with the same name, False otherwise
    """

    sidecar = Path(fileName.parent) / Path(fileName.stem).with_suffix(".aae")
    # for some reason, sometimes they append an 'O' to the name of the file?
    sidecarO = (Path(fileName.parent) / Path(fileName.stem + "O")).with_suffix(".aae")
    if sidecar.is_file():
        # debugPrint(lvl.OK, f"sidecar for {fileName.stem}{fileName.suffix} found")
        return True
    elif sidecarO.is_file():
        # debugPrint(lvl.OK, f"sidecar for {fileName.stem}{fileName.suffix} found (with O suffix)")
        return True
    else:
        # debugPrint(lvl.ERROR, f"No sidecar for {fileName} / {fileName.stem}{fileName.suffix}")
        return False


####
# The important stuff! This are the functions that provide the functionality of this
# module.
####


def fixDateless(
    jsonData: OrderedDict[str, metadataDict], filesToFix: List[str], photosFolder: Path, inferMethod: str, tag: str = ""
) -> None:
    """
    TODO: EDIT
    Adds dates of creation to all the files marked as dateless in a JSON.
    NOTE: Edits a JSON file and the photo/video file.
    Finds all the files marked as "dateless" in a JSON file, and offers all the "date" elemens in the file plus the
    inferred date of creation based on previous "dated" files. You can pick one date, and that is applied as new date
    for all the date elements present, plus it creates a CreateDate tag if none existed
    of creation for them and removes their "dateless-ness"

    Args:
        jsonFile: the path to the JSON contaning the files and their metadata
        photosFolder: the path to the root folder, used to obtain jsonFile
    """
    filesInFolder: List[Path] = getListOfFiles(photosFolder)
    # Sorting the file lists, as all the work is based on the order of these files in the hard drive
    filesInFolder = natsorted(filesInFolder)
    pathsToFix = (photosFolder / file for file in filesToFix)
    pathsToFix = natsorted(pathsToFix)

    # SHOW PROGRESS
    totalNumFiles: int = len(pathsToFix)

    # For each file that has the atribute dateless, either:
    # 1) get all the dates present in the file, print them, and ask which one to use.
    # 2) infer the date from the previous file, using the filename to decide the order
    # And then proceed to overwrite the JSON metadata and the file tags with the new date
    # Finally, we replace the metadata in the file with the newly found data, so we can
    # proceed to rename
    with ExifTool() as et:
        # We loop through datelessItems, and will get a date for it with the inference method selected for each file
        changesDict: dict[str, str] = dict()
        # Build changesDict, a dict with a date for each file, and print in screen. We will ask if we are happy
        # with the changes before applying them
        for file_ in pathsToFix:
            # The key for the JSON file is the path to the file to fix as a string
            key = str(file_)
            newDate: str = ""
            newTime: str = ""
            if inferMethod == "fileInfer":
                newDate, newTime = inferDateFromFile(jsonData, key, filesInFolder)
            elif inferMethod == "interactive":
                newDate, newTime = inferDateInteractive(jsonData, key, filesInFolder)
            debugPrint(lvl.OK, f"Chose {newDate} {newTime}")
            jsonData[key]["date"] = newDate
            jsonData[key]["time"] = newTime
            jsonData[key]["dateless"] = False
            # Write the inferred date as a tag. Probably not the most efficient way, but
            # I don't want to overcomplicate things.
            # The value of the tag to write, concatenating newDate and newTime
            tagValue: str = newDate + " " + newTime
            # The tag to use depends on whether it's a video or a photo:
            changesDict[key] = tagValue
        # Ask if we are happy with the changes propossed
        debugPrint(lvl.WARNING, "Are you happy with these dates? (y/n or p if you want to print a list of changes)")
        response = input()
        if response == "p":
            for key in changesDict:
                debugPrint(lvl.INFO, f"{Path(key).name} -> {changesDict[key]}")
        elif response != "y":
            return  # nothing to do, return from function now
        # Else, apply the changes
        with alive_bar(totalNumFiles) as bar:
            for key in changesDict:
                bar()
                if (file_.suffix).lower() in (photoExtensions + videoExtensions):
                    # Replace all time tags THAT EXIST (don't create new ones) with newDate
                    if not executeExifTool(
                        et, ["-ee", "-wm", "w", f"-time:all={changesDict[key]}", "-overwrite_original", key]
                    ):
                        debugPrint(lvl.ERROR, f"Error overwriting date tags on {Path(key).name}")
                    # If there is no CreateDate tag, create one and apply the value
                    if not executeExifTool(et, [f"-CreateDate={changesDict[key]}", "-overwrite_original", key]):
                        debugPrint(lvl.ERROR, f"Error overwriting date tags on {Path(key).name}")
                else:
                    debugPrint(lvl.ERROR, f"Unhandled case for {Path(key).name}")
    # All files must have dates now. Reorder dictionary with the new changes, and store in
    # the JSON file
    jsonData = orderDictByDate(jsonData)
    with open(jsonFileName, "w+") as write_file:
        dump(jsonData, write_file)


def doExifToolBatchProcessing(path: Path, progressBar) -> None:
    """
    Processes a folder with ExifTool and gathers a list of tags for each file

    Args:
        path: a Path to the folder to process

    """
    files = getListOfFiles(path)
    files = natsorted(files)
    debugPrint(lvl.OK, f"Found {len(files)} files")

    # # Do batch processing with ExifTool: extract all the relevant tags for our files
    start = time()
    with ExifTool() as et:
        # Data to extract:
        # CreateDate: time the file was written to flash (there's also DateTimeOriginal, which is when the shutter was actuated!)
        # MediaCreateDate: alternative for video files to CreateDate, if that's missing
        # Make and Model: used to determine if the doc comes from a "camera" or an "app"
        etData: List = et.execute_json(*tagsToExtract, str(path), "-r")
    debugPrint(lvl.OK, f"Processed {len(files)} files in {time() - start:0.02f}s")

    with open(etJSON, "w+") as writeFile:
        dump(etData, writeFile)


def generateSortedJSON(path: Path) -> None:
    """
    Generates a JSON file with keys for each file in the path passed as argument, recursively
    The entries are sorted by date and time of creation.

    This file will be consumed in a mass rename process.

    Args:
        path (Path): the directory to check for files
    """

    etData = OrderedDict()
    with open(etJSON, "r") as readFile:
        etData = load(readFile)

    # Create a JSON String with the data needed for the renaming process
    # See the metadataDict class for more info on the values
    # {
    #     "fileA": {
    #         "date": "2016-05-28",
    #         "time": "15:23:43",
    #         "hasSidecar": True
    #         [...]
    #     },
    #     "fileB": {
    #         "date": "2016-05-29",
    #         "time": "17:26:43",
    #         "hasSidecar": False
    #         [...]
    #     }
    #     [...]
    # }
    # Create the JSON structure. Use a OrderedDict for it
    # A OrderedDict using filenames as keys and date of creation as value
    jsonData: OrderedDict[str, metadataDict] = OrderedDict()

    for entry in etData:
        file: Path = Path(entry["SourceFile"])
        # The batch processor of ExifTool processes all files in folder, so remove
        # known bad extensions
        if file.suffix.lower() not in dontProcessExtensions:
            date_: str = ""
            time_: str = ""
            isDatelessFlag: bool = False
            # Get the screenshot value
            isScreenShotFlag: bool = isScreenShot(file, entry)
            # Has Manufacturer info?
            hasManufacturerFlag: bool = hasManufacturer(file, entry)
            # Get the hasSidecar value
            hasSidecarFlag: bool = hasSidecar(file)
            # Get time and date of creation
            # Extract time for Images
            if file.suffix.lower() in photoExtensions:
                date_, isDatelessFlag = findCreationTime(file, entry, photoTagsToCheck)
            # Extract time for Video
            elif file.suffix.lower() in videoExtensions:
                date_, isDatelessFlag = findCreationTime(file, entry, videoTagsToCheck)

            try:
                date_, time_ = date_.split()
            except ValueError:
                print(f"{file.name} {date_}")

            item: metadataDict = {
                "date": date_,
                "time": time_,
                "dateless": isDatelessFlag,
                "screenshot": isScreenShotFlag,
                "hasSidecar": hasSidecarFlag,
                "hasManufacturer": hasManufacturerFlag,
            }
            jsonData[entry["SourceFile"]] = item

    # This sorts the dict based on the date of creation value (date, then time) of its keys
    jsonData = orderDictByDate(jsonData)
    with open(jsonFileName, "w+") as write_file:
        dump(jsonData, write_file)


# Used to keep track of directory changes when traversing the FS
oldDirectory: Path = Path()


def massRenamer(
    jsonData: OrderedDict[str, metadataDict],
    photosDir: Path,
    isDryRun: bool = False,
    namePattern: str = "iPhone",
    selectionSubfolder: str = "",
) -> None:
    """
    Performs a mass rename based on the contents of a JSON file generated on a previous
    step.

    Args:
        fileName: the path to the folder containing the JSON file with the files to rename
        isDryRun: a debugging bool flag. If true, no rename ops are performed, just printed
        on screen. False by default (perform rename by default)
        namePatter: the string pattern to use to rename the files, "iPhone" if none passed.
    """
    # Date Histogram:
    # Find how many entries share the same date. We want to know this to figure out
    # how many zeroes the file index will have, so they are naturally sorted in the
    # file explorer
    dateHistogram = Counter(jsonData[key]["date"] for key in jsonData)

    # Counter used to name the files, starts on 1, and increases for each file with the
    # same capture date
    # One for no
    counter: int = 1
    # String used to find when the date changes
    prevDateStr: str = ""
    for key in jsonData:
        dateStr = jsonData[key]["date"]
        numberOfZeroes = len(str(dateHistogram[dateStr]))
        # debugPrint(lvl.INFO, f"{dateStr} has {dateHistogram[dateStr]} files")
        # Check the current date, and if it's the same as the previous one, increase counter. Otherwise, reset it to 1
        if dateStr == prevDateStr:
            counter += 1
        else:
            counter = 1

        # This is the list of files we are going to hanlde:
        # Store the current file and the name the file will have after the rename, as Paths
        currentFile = Path(key)
        renamedFile = (
            photosDir
            / selectionSubfolder
            / f"{dateStr.replace(':', '-')} - {namePattern} {counter:>0{numberOfZeroes}}{currentFile.suffix}"
        )

        if not renamedFile.parent.is_dir():
            debugPrint(lvl.DEBUG, f"Creating {renamedFile.parent} folder")
            renamedFile.parent.mkdir(parents=True, exist_ok=True)
        # Check if the file has a sidecar. They have the same filename than their parent file
        # with .aae extension, but sometimes they have an 'O' at the end of the name ¯\_(ツ)_/¯
        sidecarPath: Path = Path()
        renamedSidecarPath = renamedFile.with_suffix(".aae")

        # Print the name of the folder, if it's the first file in this folder we process
        global oldDirectory
        if currentFile.parent != oldDirectory:
            debugPrint(lvl.INFO, f"In {currentFile.parent}:")
        oldDirectory = currentFile.parent  # and remember current folder for next run

        if jsonData[key]["hasSidecar"]:
            # Sometimes the sidecar has O at the end of the filename (most of the times), sometimes
            # it doesn't. If the file with the O doesn't exist, try without it
            sidecarPath = currentFile.parent / f"{currentFile.stem}O.aae"
            if not sidecarPath.is_file():
                # debugPrint(lvl.ERROR, "NO SIDECAR FOUND WITH O.aae, trying without O")
                sidecarPath = currentFile.parent / f"{currentFile.stem}.aae"
                if not sidecarPath.is_file():
                    debugPrint(lvl.ERROR, "NO SIDECAR FOUND WITH OR WITHOUT O.aae PATTERN")
                else:
                    # debugPrint(lvl.OK, "SIDECAR FOUND WITH O.aae pattern")
                    pass  # leaving this in case I want to enable the debug log
            else:
                # debugPrint(lvl.OK, "SIDECAR FOUND WITH O.aae pattern")
                pass  # leaving this in case I want to enable the debug log

        # Check if the file exists before doing anything on it. This is useful to skip files that
        # have been processed in previous passes, without having to recreate the JSON file
        # Print the folder name the first time we see a "new folder"
        if isDryRun == False:
            # It's time to rename the files...
            if currentFile.is_file():
                # if file exists, rename (maybe was renamed on previous runs)
                currentFile.replace(renamedFile)
            if sidecarPath.is_file():
                debugPrint(lvl.INFO, f"Trying with sidecar {sidecarPath.name} for file {renamedFile.name}")
                sidecarPath.replace(renamedSidecarPath)
        else:
            # If dry-run is used, only print name changes
            print(lvl.OK + f"File Name: {currentFile.name}\t->\t" + lvl.WARNING + f"{renamedFile.name}")
            if jsonData[key]["hasSidecar"]:
                debugPrint(lvl.ERROR, f"\t And also rename sidecar {sidecarPath.name} to {renamedSidecarPath.name}")
        prevDateStr = dateStr


def showAllTags(fileName: Path) -> None:
    """Shows all tags for a pased file"""
    with ExifToolHelper() as eth:
        fmetadata = eth.get_metadata(str(fileName))
        debugPrint(lvl.ERROR, f"File is {fileName}")
        for data in fmetadata:
            for key, value in data.items():
                debugPrint(lvl.OK, f"{key}\t{value}")
            if "EXIF:DateTimeOriginal" in data:
                debugPrint(lvl.DEBUG, f"{data['SourceFile']}\t{data['EXIF:DateTimeOriginal']}")
            elif "File:FileModifyDate" in data:
                debugPrint(lvl.DEBUG, f"{data['SourceFile']}\t{data['File:FileModifyDate']}")
            else:
                debugPrint(lvl.DEBUG, f"{fileName} has no DateTimeOriginal tag")


def printAllDates(file: Path) -> None:
    with ExifTool() as et:
        print(et.execute("-time:all", "-G1", "-a", "-s", str(file)))


def test():
    # # Grab all tags needed
    # files = getListOfFiles(path)
    # files = natsorted(files)
    # debugPrint(lvl.OK, f"Found {len(files)} files")
    # # Do batch processing with ExifTool: extract all the relevant tags for our files
    # start = time()
    # with ExifTool() as et:
    #     # Data to extract:
    #     # CreateDate: time the file was written to flash (there's also DateTimeOriginal, which is when the shutter was actuated!)
    #     # MediaCreateDate: alternative for video files to CreateDate, if that's missing
    #     etData: List = et.execute_json("-XMP:UserComment", "-CreateDate", "-MediaCreareDate", str(path), "-r")
    # debugPrint(lvl.OK, f"Processed {len(files)} files in {time() - start:0.02f}s")
    # JSON file exists, process it. Pass the dryRun flag

    etData: List[OrderedDict] = []
    with open(etJSON, "r") as readFile:
        etData = load(readFile)

    keyList: List[str] = []
    makeList: List[str] = []
    modelList: List[str] = []
    softwareList: List[str] = []
    for item in etData:
        for key in item.keys():
            if key not in keyList:
                keyList.append(key)
            if "Make" in key and key not in makeList:
                makeList.append(key)
            if "Model" in key and key not in modelList:
                modelList.append(key)
            if "Software" in key and key not in softwareList:
                softwareList.append(key)

    # print(keyList)
    # print(makeList)
    # print(modelList)
    # print(softwareList)
    usedSW: List[str] = []
    for item in etData:
        photoMake: str = ""
        photoModel: str = ""
        photoSoftware: str = ""
        for make in makeList:
            if photoMake == "" and make in item:
                photoMake = item[make]
        for model in modelList:
            if photoModel == "" and model in item:
                photoModel = item[model]
        for software in softwareList:
            if photoSoftware == "" and software in item:
                photoSoftware = item[software]
                if "adobe" in str(photoSoftware).lower():
                    debugPrint(lvl.DEBUG, f"{item['SourceFile']}")
                if photoSoftware not in usedSW:
                    usedSW.append(photoSoftware)

        if photoMake != "" and photoMake != "Apple":
            debugPrint(lvl.INFO, f"{item['SourceFile']}: {photoMake} and {photoModel}")
        # if photoSoftware != "" and p
    usedSW = natsorted(usedSW)

    # Date Histogram:
    # Find how many entries share the same date. We want to know this to figure out
    # how many zeroes the file index will have, so they are naturally sorted in the
    # file explorer
    dateHistogram: dict = Counter()
    for software in softwareList:
        dateHistogram.update(item[software] for item in etData if software in item)

    dateHistogram = OrderedDict(sorted(dateHistogram.items(), key=lambda item: item[1]))

    # for key in dateHistogram:
    #     debugPrint(lvl.OK, f"{key}\t -> \t{dateHistogram[key]}")


# Class Experiment


class MediaFile:
    """
    A class to represent any media file (video or photo)

    Instance Attributes:
    --------------------
    _fileName: Path
        filename of the media file
    _date: str
        The date of creation: string with format YYYY:MM:DD (default: "")
    _time: str
        The time of creation: string with format HH:MM:SS (default: "")
    _isDateless: bool
        Flag to indicate if the object has no date (default: True)
    _hasSidecar: bool
        Flag to indicate if object has sidecar (default: False)
    _source: str
        Origin of the file: iPhone, WhatsApp, screenshot, camera... (default: "")

    Methods:
    --------
    """

    def __init__(self, fileName: Path, date: str, time: str, isDateless: bool, source: str):
        """
        Attributes:
        -----------
        _fileName: Path
            filename of the media file
        _date: str
            The date of creation: string with format YYYY:MM:DD (default: "")
        _time: str
            The time of creation: string with format HH:MM:SS (default: "")
        _isDateless: bool
            Flag to indicate if the object has no date (default: True)
        _sidecar: Path
            If the file has a sidecar, path to it, or empty path if it doesn't have one (default: "")
        _source: str
            Origin of the file: iPhone, WhatsApp, screenshot, camera... (default: "")
        """
        self_filename: Path = fileName
        self._date: str = date
        self._time: str = time
        self._isDateless: bool = isDateless
        self._sidecar: bool = hasSidecar(fileName)
        self._source: str = source


class PhotoFile(MediaFile):
    def __init__(self, etTagsDict: Dict[str, str]):
        """
        Parameters:
            etTagsDict: Dict[str, str]
                A dictionary with a collection of tags, provided by ExifTool
        """
