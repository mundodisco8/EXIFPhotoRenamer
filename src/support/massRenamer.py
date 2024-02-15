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
    "folder\\2 May 2018 - 3 of 185.heic": {
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
    Photos on Mac exported them with an extra `O` in the name, before the extension ¯\_(ツ)_/¯)
    generateSortedJSON: loops through a folder and generates a JSON file with the images/videos
    on it, and the metadata needed in the renaming process
"""
from datetime import datetime
from exiftool import ExifToolHelper
from json import dump, load
from pathlib import Path
from re import compile
from typing import Dict, Tuple
from .support import lvl, debugPrint

# Use this to remember folder names, and print them only once
prevDirectory: str = ""
def findCreationTime(file: Path)->Tuple[str,str,str]:
    """Returns the Creation Time and Date (in the local time) of creation of a file
    with EXIF data and the time offset respect UTC

    Args:
        file (Path): a Pathlib path to the file to check

    Returns:
        list: a list of three strings, with the date, time and offset from UTC.
    """

    date: str = ""
    time: str = ""
    offset: str = ""

    # Searches for "[+/-]XX:XX" where XX:XX is time in HH:MM
    offsetRegEx = compile(r'[\+\-][0-9]{2}\:[0-9]{2}')
    # Print folder name, if != than previous time we called it
    global prevDirectory
    if file.parent != prevDirectory:
        debugPrint(lvl.DEBUG, f"In {file.parent}:")
    prevDirectory = file.parent # and remember current folder for next run

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
                offset = d['EXIF:OffsetTime']

        if date == "":
            raise TypeError("No date found on file!!!")

        # Print the value that will be used as the date
        # The value can be in "YYYY:mm:DD HH:MM:SS" or "YYYY:mm:DD HH:MM:SS[+-]OO:OO"
        # where [+-]OO:OO is an offset from UTC. For example: [date] 15:42:23+01:00 means
        # the picture was taken at 15:42:23 local time, 14:42:23 UTC
        # Becase we want to sort based on local time, we will strip that info, if found
        debugPrint(lvl.INFO, f"{file.stem}{file.suffix}\t{date}")

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
            # debugPrint(lvl.ERROR, "NO OFFSET")
            pass
        # Commenting as probably will be too verbosy otherwise
        # else:
            # debugPrint(lvl.DEBUG, "No OFFSET on File")
        # split
        date, time = date.split()
        if time == "":
            raise TypeError("No Time found on file!!!")
    return date, time, offset

def hasSidecar(fileName: Path)->bool:
    """Finds if a file has a sidecar associated with it
    For an image with name pattern `name.ext`, sidecars have the name pattern of:
    `nameO.aae`


    Args:
        fileName (Path): a Path to the file to check for sidecars

    Returns:
        True if there's a sidecar with the same name, False otherwise
    """
    # Strip path in filename and ext
    # Complete path + filename + ext
    # debugPrint(lvl.OK, f"Full path {fileName}")
    # filename only
    # debugPrint(lvl.WARNING, f"Filename {fileName.stem}")
    # extension only
    # debugPrint(lvl.ERROR, f"Extension {fileName.suffix}")
    # Just the directory path of the file
    # debugPrint(lvl.OK, f"Parent {fileName.parent}")
    sidecar = (Path(fileName.parent) / Path(fileName.stem + "O")).with_suffix(".aae")
    if sidecar.is_file():
        # debugPrint(lvl.OK, f"sidecar for {fileName.stem}{fileName.suffix} found")
        return True
    else:
        # debugPrint(lvl.ERROR, f"No sidecar for {fileName.stem}{fileName.suffix}")
        return False

def generateSortedJSON(path: Path)->None:
    """
    Generates a JSON file with keys for each file in the path passed as argument, recursively
    The entries are sorted by date and time of creation.

    This file will be consumed in a mass rename process.

    Args:
        path (Path): the directory to check for files
    """
    # List comprehension: every file in photosDir, recursively, if the file is "a file" and it's not .DS_Store or a sidecar
    files = [file for file in path.rglob("*") if file.is_file() and (file.stem != ".DS_Store" and file.suffix != ".aae")]
    sidecars = list(path.rglob('*.aae'))
    if sidecars:
        debugPrint(lvl.WARNING, f"There are {len(sidecars)} sidecars")
        for sidecar in sidecars:
            debugPrint(lvl.WARNING, f"\t{sidecar}")
    else:
        debugPrint(lvl.WARNING, "No Sidecars in folder")

    debugPrint(lvl.OK, f"Found {len(files)} files")

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

# As prevDirectory above, but with another name. Plays the same function
oldDirectory: str = ""
def massRenamer(fileName: Path, isDryRun: bool = False, namePattern: str = "iPhone")->None:
    """
    Performs a mass rename based on the contents of a JSON file generated on a previous
    step.

    Args:
        fileName: the path to the folder containing the JSON file with the files to rename
        isDryRun: a debugging bool flag. If true, no rename ops are performed, just printed
        on screen. False by default (perform rename by default)
        namePatter: the string pattern to use to rename the files, "iPhone" if none passed.
    """
    with open(fileName, "r") as readFile:
        jsonData = load(readFile)

    # Counter used to name the files, starts on 1, and increases for each file with the
    # same capture date
    counter: int = 1
    # String used to find when the date changes
    prevDateStr: str = ""

    for key in jsonData:
        # Convert string to datetime object, and then back to string. Can probably made easier
        # but hey!
        dateObj = datetime.strptime(jsonData[key]['date'], "%Y:%m:%d")
        dateStr = datetime.strftime(dateObj, "%Y-%m-%d")

        # Check the current date, and if it's the same as the previous one, increase counter. Otherwise, reset it to 1
        if dateStr == prevDateStr:
            counter += 1
        else:
            counter = 1

        # This is the list of files we are going to hanlde:
        # Store the current file and the name the file will have after the rename, as Paths
        currentFile = Path(key)
        renamedFile = currentFile.parent / f"{dateStr} - {namePattern} {counter}{currentFile.suffix}"
        # Check if the file has a sidecar. They have the same filename than their parent file
        # with .aae extension, but sometimes they have an 'O' at the end of the name ¯\_(ツ)_/¯
        sidecarPath: Path = Path()
        renamedSidecarPath = renamedFile.with_suffix(".aae")

        # Print the name of the folder, if it's the first file in this folder we process
        global oldDirectory
        if currentFile.parent != oldDirectory:
            debugPrint(lvl.INFO, f"In {currentFile.parent}:")
        oldDirectory = currentFile.parent # and remember current folder for next run

        if jsonData[key]['hasSidecar']:
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
                    pass # leaving this in case I want to enable the debug log
            else:
                # debugPrint(lvl.OK, "SIDECAR FOUND WITH O.aae pattern")
                pass # leaving this in case I want to enable the debug log

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
            if jsonData[key]['hasSidecar']:
                debugPrint(lvl.ERROR, f"\t And also rename sidecar {sidecarPath.name} to {renamedSidecarPath.name}")
        prevDateStr = dateStr


def showAllTags(fileName: Path)->None:
    """Shows all tags for a pased file"""
    with ExifToolHelper() as eth:
        fmetadata = eth.get_metadata(fileName)
        debugPrint(lvl.ERROR, f"File is {fileName}")
        for data in fmetadata:
            for key, value in data.items():
                debugPrint(lvl.OK, f"{key}\t{value}")
            if "EXIF:DateTimeOriginal" in data:
                debugPrint(lvl.DEBUG, f"{data['SourceFile']}\t{data['EXIF:DateTimeOriginal']}")
            elif "File:FileModifyDate" in data:
                debugPrint(lvl.DEBUG, f"{data['SourceFile']}\t{data['File:FileModifyDate']}")
            else:
                debugPrint(
                    lvl.DEBUG, f"{fileName} has no DateTimeOriginal tag")