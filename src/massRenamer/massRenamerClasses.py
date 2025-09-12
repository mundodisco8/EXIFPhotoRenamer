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

from subprocess import PIPE, run
from json import load, JSONDecodeError, dumps
from pathlib import Path
from re import compile, search, match
from logging import getLogger

from natsort import os_sorted
from tzfpy import get_tz
from whenever import OffsetDateTime, PlainDateTime, TimeDelta, ZonedDateTime

module_logger = getLogger(__name__)

# Filename for the JSON file to use

# Filename to use the metadata obtained from the ExifTool batch processing
etJSON: Path = Path("etJSON.json")
objectFile: Path = Path("MediaFileList.txt")

# list of image extensions:
IMAGE_EXTENSIONS: list[str] = [".jpeg", ".jpg", ".png", ".heic"]
VIDEO_EXTENSIONS: list[str] = [".mov", ".mp4"]
# List of file extensions to ignore, as EXIFTool generates empty tags for them.
DONT_PROCESS_EXTENSIONS: list[str] = [".aae", ".ds_store", ".json", ".zip"]

##
# Compiled Regexes
##

# GPS coordinates
GPSCoordsRegEx = compile(r"([0-9]+) deg ([0-9]+)' ([0-9.]+)\"")

####
# Creation date finder - findCreationTime
####

# These are the tags that I'm capturing with EXIFTool about creation time
dateTagsToCheck: list[str] = [
    "ExifIFD:DateTimeOriginal",
    "QuickTime:DateTimeOriginal",
    "XMP:DateTimeOriginal",
    "ExifIFD:CreateDate",
    "QuickTime:CreateDate",
    "PNG:CreateDate",
    "XMP:CreateDate",
    "QuickTime: CreationDate",
    "XMP-photoshop:DateCreated",  # in some iPhone pngs...
]

# This dict contains the correct offset tag for each time tag
offsetDict: dict[str, str] = {
    "ExifIFD:DateTimeOriginal": "ExifIFD:OffsetTimeOriginal",
    "ExifIFD:CreateDate": "ExifIFD:OffsetTimeDigitized",
    "ExifIFD:ModifyDate": "ExifIFD:OffsetTime",
}

# List of GPS tags to grab metadata from
GPSTagsList: list[str] = [
    "GPSLatitudeRef",
    "GPSLatitude",
    "GPSLongitudeRef",
    "GPSLongitude",
]


# NOTE: Tested
def findCreationTime(exifToolData: dict[str, str]) -> str | None:
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

    # We are asking EXIFTool to return the dates in `YYYY-MM-DDThh:mm:ss⨦oo:00` format. If the tag has offset info,
    # then obviously the offset is correct, but sometimes it returns +00:00 and then you have to check the presence of
    # offset tags.
    # From ExifTool (https://exiftool.org/TagNames/EXIF.html)
    #
    # 0x9003    DateTimeOriginal        string  ExifIFD     (date/time when original image was taken)
    # 0x9004    CreateDate              string  ExifIFD     (called DateTimeDigitized by the EXIF spec.)
    # 0x9010    OffsetTime              string  ExifIFD     (time zone for ModifyDate)
    # 0x9011    OffsetTimeOriginal      string  ExifIFD     (time zone for DateTimeOriginal)
    # 0x9012    OffsetTimeDigitized     string  ExifIFD     (time zone for CreateDate)

    # Loop through the dateTagsToCheck tags. They are sorted by preference. As soon as we have one, we can take that one
    # as the date and break
    date: ZonedDateTime | OffsetDateTime | PlainDateTime | None = None
    for tag in dateTagsToCheck:
        if tag in exifToolData:
            # Ideally, we got a date in the format YYYY-MM-DDThh:mm:ss±OO:OO, that we can parse as OffsetDateTime
            try:
                date = OffsetDateTime.parse_common_iso(exifToolData[tag])
            except ValueError:
                # But it might not have offset, so try as PlainDateTime
                try:
                    date = PlainDateTime.parse_common_iso(exifToolData[tag]).assume_fixed_offset(0)
                except ValueError:
                    # At least in Quicktime tags, instead of deleting the tags, they are set to "0000:00:00 00:00:00"
                    # which I think fails as that is not a "date" (whenever only accepts 1-1-1 first date)
                    if exifToolData[tag] == "0000:00:00 00:00:00":
                        # I could delete the tag, but I don't have access to the source, just a copy of it
                        pass
                    else:
                        raise

            # At this point, we have a date with an offset, or the date didn't have offset and we assumed UTC.
            # Nevertheless, if there are GPS tags, we can get the timezone from it (more precise) or there might be
            # offset tags to check too. We'll give preference to the GPS as it's absolute (the offset tag requires
            # having set the time and date correctly, obviously)
            if (
                "GPS:GPSLatitudeRef" in exifToolData.keys()
                and "GPS:GPSLatitude" in exifToolData.keys()
                and "GPS:GPSLongitudeRef" in exifToolData.keys()
                and "GPS:GPSLongitude" in exifToolData.keys()
            ):
                # Latitude and longitude follow the "GGG deg MM' SS.00"" format, we have a regexp to capture the numbers
                longMatch = match(GPSCoordsRegEx, exifToolData["GPS:GPSLongitude"])
                latMatch = match(GPSCoordsRegEx, exifToolData["GPS:GPSLatitude"])
                longitude: float | None = None
                latitude: float | None = None
                if longMatch:
                    # Got degrees, minutes and seconds in match groups 1, 2 and 3
                    longitude = (
                        int(longMatch.group(1)) + (int(longMatch.group(2)) / 60) + (float(longMatch.group(3)) / 3600)
                    )
                    if exifToolData["GPS:GPSLongitudeRef"] == "West":
                        # If coordinates are South, then they are negative
                        longitude *= -1
                if latMatch:
                    latitude = (
                        int(latMatch.group(1)) + (int(latMatch.group(2)) / 60) + (float(latMatch.group(3)) / 3600)
                    )
                    if exifToolData["GPS:GPSLatitudeRef"] == "South":
                        # If coordinates are West, then they are negative
                        latitude *= -1

                if longitude and latitude:
                    myTZ = get_tz(longitude, latitude)
                    # Type dance: convert to plain (to get rid of whatever offset it had), assume it belongs to tz, so
                    # we have a time with the same "value" but on a different tz, and then to fixed offset (as we
                    # can't store the timezone string in the tags)
                    date = date.to_tz(myTZ).to_fixed_offset()
            else:
                # No GPS location, try offsets
                if tag in offsetDict.keys() and offsetDict[tag] in exifToolData.keys():
                    offsetStr = exifToolData[offsetDict[tag]]
                    if len(offsetStr) != 6:
                        # Offset has to be ±HH:MM
                        raise ValueError(f"Offset ({offsetStr}) is the wrong length")
                    offsetSign = offsetStr[0]  # + or -
                    offsetHours = offsetStr[1:3]  # HH
                    offsetMin = offsetStr[4:]  # skip : and get MM

                    # "Delete" the current offset by considering the date a plain date, and then create a new fixed offset
                    # By passing the offset as a "TimeDelta" we can pass "fractional" offsets (01:30). To get a negative
                    # offset, we have to pass "negative" hours and "negative" minutes (otherwise they cancel each other
                    # out: -2h and +30 minutes is -01:30)
                    offsetTimeDelta = TimeDelta(
                        hours=int(offsetSign + offsetHours), minutes=int(offsetSign + offsetMin)
                    )
                    # Type dance: convert to plain (to get rid of whatever offset it had), assume it has a certain fixed
                    # offset, so we have a time with the same "value" but on a different offset.
                    date = date.to_plain().assume_fixed_offset(offsetTimeDelta)
            break

    if date:
        return date.format_common_iso()
    return None


####
# File Source finders: determines the source of different types of files
####


# NOTE: Tested
def isScreenShot(exifToolData: dict[str, str]) -> bool:
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
            if not isScreenShotFlag and "screenshot" in exifToolData[key].lower():
                isScreenShotFlag = True
    # Else, no "comment" keys, return false

    return isScreenShotFlag


# NOTE: Tested
def isInstaOrFace(exifToolData: dict[str, str]) -> bool:
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
            if not isInstaFlag and "facebook" in exifToolData[key].lower() or "instagram" in exifToolData[key].lower():
                isInstaFlag = True

    return isInstaFlag


# NOTE: Tested
def isPicsArt(exifToolData: dict[str, str]) -> bool:
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
def getFileSource(exifToolData: dict[str, str]) -> str:
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
        modelKeyList: list[str] = [key for key in exifToolData if "model" in key.lower()]
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
        makeKeyList: list[str] = [key for key in exifToolData if "make" in key.lower()]
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


class MediaFile:
    """
    A class to represent any media file (video or photo)

    Instance Attributes:
    --------------------
    fileName: Path
        filename of the media file
    dateTime: str
        The date of creation: string with format YYYY:MM:DD HH:MM:SS+OO:OO(default: "")
    hasSidecar: bool
        Flag to indicate if object has sidecar (default: False)
    source: str
        Origin of the file: iPhone, WhatsApp, screenshot, camera... (default: "")
    EXIFTags: dict[str, str]
        A list of the tags for the file found by EXIFTool. It can come handy at some point and it only takes a little
        bit of memory to keep them (while re-scanning takes quite a while).

    Methods:
    --------
    fromExifTags

    """

    # Use slots, instead of a dict, for the attributes. This makes the attribs static, but require less memory per
    # object and has faster access
    __slots__ = "fileName", "dateTime", "source", "sidecar", "EXIFTags"

    # NOTE: Tested
    def __init__(self, fileName: Path, dateTime: str | None, source: str, EXIFTags: dict[str, str] | None = None):
        """
        Attributes:
        -----------
        fileName: Path
            filename of the media file
        dateTime: str
            The date and time of creation: string with format 'YYYY-MM-DDThh:mm:ss±OO:OO', or
            None if it has not been determined yet.
        source: str
            Origin of the file: iPhone, WhatsApp, screenshot, camera... (default: "")
        sidecar: Path
            A path to a sidecar file for this media, if available, or None otherwise
        tags: dict[str, str]
            The list of tags that ExifTool found for this file. Stored for convenienve in case we want to check them
            later without having to spin another ExifTool (for example, to check the dates available in the file).
        """
        self.fileName: Path = fileName
        # TODO: do some sort of datetime string validation here?
        self.dateTime: str | None = dateTime
        self.sidecar: Path | None = getSidecar(fileName)
        self.source: str = source
        self.EXIFTags: dict[str, str] = EXIFTags or {}

    @classmethod
    def fromExifTags(cls, etTagsDict: dict[str, str]):
        """Class method to get a instance from a list of tags from ExifTool

        Args:
            etTagsDict (dict[str, str]): a dictionary with the output of Exiftool as a JSON

        Returns:
            _type_: if the dictionary passed has the required tags, an instance of MediaFile. Raises an exception
            otherwise.
        """
        # Get the filename for the object
        try:
            filename_: Path = Path(etTagsDict["SourceFile"])
        except KeyError:
            print(f"No SourceFile tag in the EXIF metadata! -> {etTagsDict}")
            raise
        # Try to find a date of creation, if available in the passed tags
        dateTime_: str | None = findCreationTime(etTagsDict)
        #
        #  Find the source
        try:
            source_: str = getFileSource(etTagsDict)
        except KeyError:
            print("Error")
            raise

        return cls(fileName=filename_, dateTime=dateTime_, source=source_, EXIFTags=etTagsDict)

    # NOTE: Tested
    def __repr__(self):
        """
        Returns a string with the representation of the object: this string could be used to init an instance
        Example: MediaFile(fileName='Name', dateTime='1234-12-12 11-22-33+03:00', source="Apple iPhone 8")
        """
        return f'{type(self).__name__}(fileName=Path("{self.fileName}"), dateTime="{self.dateTime}", source="{self.source}", EXIFTags={self.EXIFTags})'


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
def loadMediaFileListFromFile(inputFile: Path) -> list[MediaFile]:
    """Loads and returns a list of MediaFile objects stored in a file passed as input

    Args:
        inputFile (Path): a file containing a list of MediaFile objects as text

    Returns:
        list[MediaFile]: a list of MediaFile objects
    """
    mediaFileList: list[MediaFile] = []
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
def storeMediaFileListTags(outputFile: Path, listMediaFiles: list[MediaFile]) -> None:
    """
    Stores the EXIT tags of a list of MediaFile in a JSON file , so it's easy to rebuild it.

    Args:
        outputFile (Path): name of the file to store the data to.
        listTags (list[MediaFile]): a list of MediaFile objects.
    """
    with open(outputFile, "w") as writeFile:
        writeFile.write("[")
        writeFile.write(",".join([dumps(instance.EXIFTags) for instance in listMediaFiles]))
        # for instance in listMediaFiles:
        #     writeFile.write(dumps(instance.EXIFTags))
        #     writeFile.write(",")
        writeFile.write("]")


# NOTE: Tested
def loadExifToolTagsFromFile(inputFile: Path) -> list[dict[str, str]]:
    """
    Reads the output file from the EXIFTool batch processing (a collection of EXIF
    tags).

    The input JSON file contains tags from EXIFTool.
    NOTE: be careful with paths!

    Args:
        inputFile (Path): path to the file containing the output of ExifTool

    Returns:
        list[dict[str, str]]: a list of dictionaries with the tags for each file.
    """
    etData: list[dict[str, str]] = []
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
def storeExifToolTags(outputFile: Path, listTags: list[dict[str, str]]) -> None:
    """
    Stores the list tags passed as parameter in the file specified

    Args:
        outputFile (Path): name of the file to store the data to.
        listTags (list[dict[str,str]]): a list of dictionaries, containing the EXIF tags
        as key-value pairs, from EXIFTool
    """

    with open(outputFile, "w") as writeFile:
        writeFile.write(str(listTags))


# NOTE: Tested
def generateSortedMediaFileList(etData: list[dict[str, str]]) -> list[MediaFile]:
    """
    Creates a list of MediaFile objects from a list of dictionaries with tags comming from
    EXIFTool. The list is sorted by filename using natural sorting (as in "Windows Explorer Sorting")

    Args:
        etData (list[dict[str, str]): a list of dictionaries. Each dictionary is a collection of tags
        obtained from EXIFTool

    Returns:
        list[MediaFile]: a list of MediaFile objects, ready to be processed
    """
    mediaFileList: list[MediaFile] = []

    for entry in etData:
        # The batch processor of ExifTool processes some files that are not images, so remove
        # known bad extensions. Get the filename and check its extension
        fileName: Path = Path(entry["SourceFile"])
        # We have to check 'suffix' for files with name.extension ('example.aae'), and name for files with name starting with . ('.ds_store')
        if (fileName.suffix.lower() not in DONT_PROCESS_EXTENSIONS) and (
            fileName.name.lower() not in DONT_PROCESS_EXTENSIONS
        ):
            mediaFileList.append(MediaFile.fromExifTags(entry))

    # Sorts the list based on the filename. This will help to infer dates based on
    # "neighbours" with date.
    mediaFileList = os_sorted(mediaFileList, key=lambda x: x.fileName)
    return mediaFileList


####
# Creation date fixers
####


# NOTE: Tested
def inferDateFromNeighbours(datelessMFIdx: int, mediaFileList: list[MediaFile]) -> tuple[str | None, str | None]:
    """infers the date of creation of a dateless item in a list of MediaFile, based on the file's neighbours' dates.

    The list has to be ordered by filename, otherwise the times we infer might not be very relevant

    Args:
        datelessMFIdx (int): index of the item in mediaFileList that we want to get a new date for
        mediaFileList (list[MediaFile]): a list of MediaFile objects (so we can infer the date from the neighbours)

    Returns:
        tuple[str | None, str | None]: first element of the tuple, inferred date from the "left" side, using dated
        elements that are probably older than the current element, and the second element is the inferred date on the
        "right" side (elements that should be newer than the current element).
        The returned values are a dateTime with offset as a string (`YYYY-MM-DDTHH:MM:SS±OO:OO`) or None if no dated
        item could be found on that side of the list.
    """

    inferredDateLeft: str | None = None
    inferredDateRight: str | None = None
    datedObjectIdxLeft: int | None = None
    datedObjectIdxRight: int | None = None

    ### Functional programming time!
    # We will look for the first item in the right-hand side list, split from the item passed as datelessMFIdx, that
    # has a date. We get a list of items with date using filter(), plus a lambda, and next(). And then we use
    # list.index() to get the index of that number. If no item is found or the list is empty, we
    # Boom! (almost a) One-liner!
    try:
        datedObjectIdxRight = mediaFileList.index(
            next(filter(lambda instance: instance.dateTime is not None, mediaFileList[datelessMFIdx:]))
        )
    except StopIteration:
        # The search list was an empty list (dateless item was last item of the list), or no more dated items were found
        # Leave datedObjectIdxRight as None
        pass

    # For the  left side, we reverse the search sublist
    try:
        datedObjectIdxLeft = mediaFileList.index(
            next(filter(lambda instance: instance.dateTime is not None, reversed(mediaFileList[:datelessMFIdx])))
        )
    except StopIteration:
        # The search list was an empty list (dateless item was last item of the list), or no more dated items were found
        # Leave datedObjectIdxRight as None
        pass

    # At this point, datedObjectIdxLR are not None. They are -1 if no dated item was found on that side, or >=0 if a
    # dated item was found
    if datedObjectIdxLeft is not None:
        # If the index is not None, then it's the index to a dated item
        # Complains that mediaFileList[datedObjectIdxLeft].dateTime can be None, but at this point, we know that it
        # contains a date string (otherwise we would not use it) can ignore the linting error.
        foundDateLeft = OffsetDateTime.parse_common_iso(mediaFileList[datedObjectIdxLeft].dateTime)  # pyright: ignore[reportArgumentType]
        # It's not DST safe to add time to a OffsetDateTime, but we can bypass that with ignore_dst. Please don't take
        # pictures around DST change times
        inferredDateLeft = foundDateLeft.add(
            minutes=(datelessMFIdx - datedObjectIdxLeft), ignore_dst=True
        ).format_common_iso()
    if datedObjectIdxRight is not None:
        # We can ignore the linting error because dateTime will not be None
        foundDateRight = OffsetDateTime.parse_common_iso(mediaFileList[datedObjectIdxRight].dateTime)  # pyright: ignore[reportArgumentType]
        inferredDateRight = foundDateRight.subtract(
            minutes=(datedObjectIdxRight - datelessMFIdx), ignore_dst=True
        ).format_common_iso()

    return (inferredDateLeft, inferredDateRight)


### STEP 2 Process Data and Extract


def generateMediaFileList(EXIFTagFile: Path) -> None:
    # # Being quite explicit:
    # # 1) read exif tags from file -> generate list of dicts
    # exifDicts: list[dict[str, str]] = loadExifToolTagsFromFile(EXIFTagFile)
    # # 2) Use list of dicts -> generate list of MediaFile
    # mediaList: list[MediaFile] = generateSortedMediaFileList(exifDicts)
    # print(mediaList)
    # # 3) Store MediaFile list on disk
    # storeMediaFileList(objectFile, mediaList)
    # # 4) Find Dateless, try to correct them by hand
    # dateless = [instance for instance in mediaList if instance.dateTime is None]
    # print(dateless)
    # print(f"Found {len(dateless)} {'instance' if (len(dateless) == 1) else 'instances'} without date")
    # for item in dateless:
    #     # find item in mediaList
    #     idx = mediaList.index(item)
    #     newDate = fixDateInteractive(idx, mediaList)
    #     if newDate:
    #         medialist[idx].dateTime = newDate

    # storeMediaFileList(objectFile, mediaList)

    return
