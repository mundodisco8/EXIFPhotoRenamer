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
from collections import Counter
from typing import Callable

from natsort import os_sorted
from tzfpy import get_tz
from whenever import OffsetDateTime, PlainDateTime, TimeDelta, ZonedDateTime

module_logger = getLogger(__name__)

####
# Lists
####

# list of image extensions:
IMAGE_EXTENSIONS: list[str] = [".jpeg", ".jpg", ".png", ".heic"]
VIDEO_EXTENSIONS: list[str] = [".mov", ".mp4"]
# List of file extensions to ignore, as EXIFTool generates empty tags for them.
DONT_PROCESS_EXTENSIONS: list[str] = [".aae", ".ds_store", ".json", ".zip"]

# These are all the time tags that -time:all extract. Note that these tags don't have their group attached to them
# Extracted with exiftool -list -time:all
TIME_TAGS_LIST: list[str] = [
    "ABDate",
    "AccessDate",
    "Acknowledged",
    "AcquisitionTime",
    "AcquisitionTimeDay",
    "AcquisitionTimeMonth",
    "AcquisitionTimeStamp",
    "AcquisitionTimeYear",
    "AcquisitionTimeYearMonth",
    "AcquisitionTimeYearMonthDay",
    "AppleMailDateReceived",
    "AppleMailDateSent",
    "ArtworkCircaDateCreated",
    "ArtworkDateCreated",
    "AudioModDate",
    "BackupTime",
    "Birthday",
    "BroadcastDate",
    "BroadcastTime",
    "BuildDate",
    "CFEGFlashTimeStamp",
    "CalibrationDateTime",
    "CameraDateTime",
    "CameraPoseTimestamp",
    "CaptionsDateTimeStamps",
    "CircaDateCreated",
    "ClassifyingCountryCodingMethodDate",
    "ClipCreationDateTime",
    "CommentTime",
    "ContainerLastModifyDate",
    "ContentCreateDate",
    "ContractDateTime",
    "CopyrightYear",
    "CoverDate",
    "CreateDate",
    "CreationDate",
    "CreationTime",
    "DataCreateDate",
    "DataModifyDate",
    "Date",
    "Date1",
    "Date2",
    "DateAccessed",
    "DateAcquired",
    "DateArchived",
    "DateCompleted",
    "DateCreated",
    "DateDisplayFormat",
    "DateEncoded",
    "DateIdentified",
    "DateImported",
    "DateLastSaved",
    "DateModified",
    "DatePictureTaken",
    "DatePurchased",
    "DateReceived",
    "DateRecieved",
    "DateReleased",
    "DateSent",
    "DateTagged",
    "DateTime",
    "DateTime1",
    "DateTime2",
    "DateTimeCompleted",
    "DateTimeCreated",
    "DateTimeDigitized",
    "DateTimeDropFrameFlag",
    "DateTimeDue",
    "DateTimeEmbeddedFlag",
    "DateTimeEnd",
    "DateTimeGenerated",
    "DateTimeKind",
    "DateTimeOriginal",
    "DateTimeRate",
    "DateTimeStamp",
    "DateTimeStart",
    "DateTimeUTC",
    "DateVisited",
    "DateWritten",
    "DayOfWeek",
    "DaylightSavings",
    "DeclassificationDate",
    "DeprecatedOn",
    "DerivedFromLastModifyDate",
    "DestinationCity",
    "DestinationDST",
    "DigitalCreationDate",
    "DigitalCreationDateTime",
    "DigitalCreationTime",
    "EarthPosTimestamp",
    "EmbargoDate",
    "EncodeTime",
    "EncodingTime",
    "EndTime",
    "EventAbsoluteDuration",
    "EventDate",
    "EventDay",
    "EventEarliestDate",
    "EventEndDayOfYear",
    "EventEndTimecodeOffset",
    "EventLatestDate",
    "EventMonth",
    "EventStartDayOfYear",
    "EventStartTime",
    "EventStartTimecodeOffset",
    "EventTime",
    "EventVerbatimEventDate",
    "EventYear",
    "ExceptionDateTimes",
    "ExclusivityEndDate",
    "ExpirationDate",
    "ExpirationTime",
    "ExtensionCreateDate",
    "ExtensionModifyDate",
    "FileAccessDate",
    "FileCreateDate",
    "FileInodeChangeDate",
    "FileModifyDate",
    "FilmTestResult",
    "FirstPhotoDate",
    "FirstPublicationDate",
    "FormatVersionTime",
    "GPSDateStamp",
    "GPSDateTime",
    "GPSDateTimeRaw",
    "GPSTimeStamp",
    "HistoryWhen",
    "HometownCity",
    "HometownDST",
    "HumanObservationDay",
    "HumanObservationEarliestDate",
    "HumanObservationEndDayOfYear",
    "HumanObservationEventDate",
    "HumanObservationEventTime",
    "HumanObservationLatestDate",
    "HumanObservationMonth",
    "HumanObservationStartDayOfYear",
    "HumanObservationVerbatimEventDate",
    "HumanObservationYear",
    "IPTCLastEdited",
    "ImageProcessingFileDateCreated",
    "IngredientsLastModifyDate",
    "KillDateDate",
    "LastBackupDate",
    "LastPhotoDate",
    "LastPrinted",
    "LastUpdate",
    "LayerModifyDates",
    "LicenseEndDate",
    "LicenseStartDate",
    "LicenseTransactionDate",
    "LocalCreationDateTime",
    "LocalEndDateTime",
    "LocalEventEndDateTime",
    "LocalEventStartDateTime",
    "LocalFestivalDateTime",
    "LocalLastModifyDate",
    "LocalModifyDate",
    "LocalStartDateTime",
    "LocalUserDateTime",
    "LocationDate",
    "MDItemContentCreationDate",
    "MDItemContentCreationDateRanking",
    "MDItemContentCreationDate_Ranking",
    "MDItemContentModificationDate",
    "MDItemDateAdded",
    "MDItemDateAdded_Ranking",
    "MDItemDownloadedDate",
    "MDItemFSContentChangeDate",
    "MDItemFSCreationDate",
    "MDItemGPSDateStamp",
    "MDItemInterestingDateRanking",
    "MDItemInterestingDate_Ranking",
    "MDItemLastUsedDate",
    "MDItemMailDateReceived_Ranking",
    "MDItemTimestamp",
    "MDItemUsedDates",
    "MDItemUserDownloadedDate",
    "MachineObservationDay",
    "MachineObservationEarliestDate",
    "MachineObservationEndDayOfYear",
    "MachineObservationEventDate",
    "MachineObservationEventTime",
    "MachineObservationLatestDate",
    "MachineObservationMonth",
    "MachineObservationStartDayOfYear",
    "MachineObservationVerbatimEventDate",
    "MachineObservationYear",
    "ManagedFromLastModifyDate",
    "ManifestReferenceLastModifyDate",
    "ManufactureDate",
    "ManufactureDate1",
    "ManufactureDate2",
    "MaterialAbsoluteDuration",
    "MaterialEndTimecodeOffset",
    "MeasurementDeterminedDate",
    "MediaCreateDate",
    "MediaModifyDate",
    "MediaOriginalBroadcastDateTime",
    "MetadataDate",
    "MetadataLastEdited",
    "MetadataModDate",
    "MinoltaDate",
    "MinoltaTime",
    "ModDate",
    "ModificationDate",
    "ModifyDate",
    "Month",
    "MonthDayCreated",
    "MoonPhase",
    "NikonDateTime",
    "Now",
    "ON1_SettingsMetadataCreated",
    "ON1_SettingsMetadataModified",
    "ON1_SettingsMetadataTimestamp",
    "ObjectCountryCodingMethodDate",
    "ObservationDate",
    "ObservationDateEnd",
    "ObservationTime",
    "ObservationTimeEnd",
    "OffSaleDateDate",
    "OffsetTime",
    "OffsetTimeDigitized",
    "OffsetTimeOriginal",
    "OnSaleDateDate",
    "OptionEndDate",
    "OriginalCreateDateTime",
    "OriginalReleaseTime",
    "OriginalReleaseYear",
    "OtherDate1",
    "OtherDate2",
    "OtherDate3",
    "PDBCreateDate",
    "PDBModifyDate",
    "PackageLastModifyDate",
    "PanasonicDateTime",
    "PatientBirthDate",
    "PaymentDueDateTime",
    "PhysicalMediaLength",
    "PlanePoseTimestamp",
    "PoseTimestamp",
    "PowerUpTime",
    "PreviewDate",
    "PreviewDateTime",
    "ProducedDate",
    "ProductionDate",
    "ProfileDateTime",
    "PublicationDateDate",
    "PublicationDisplayDateDate",
    "PublicationEventDate",
    "PublishDate",
    "PublishDateStart",
    "RecordedDate",
    "RecordingTime",
    "RecordingTimeDay",
    "RecordingTimeMonth",
    "RecordingTimeYear",
    "RecordingTimeYearMonth",
    "RecordingTimeYearMonthDay",
    "RecurrenceDateTimes",
    "RecurrenceRule",
    "ReelTimecode",
    "ReferenceDate",
    "RegionInfoDateRegionsValid",
    "RegisterCreationTime",
    "RegisterItemStatusChangeDateTime",
    "RegisterReleaseDateTime",
    "RegisterUserTime",
    "RelationshipEstablishedDate",
    "ReleaseDate",
    "ReleaseDateDay",
    "ReleaseDateMonth",
    "ReleaseDateYear",
    "ReleaseDateYearMonth",
    "ReleaseDateYearMonthDay",
    "ReleaseTime",
    "RenditionOfLastModifyDate",
    "RevisionDate",
    "RicohDate",
    "RightsStartDateTime",
    "RightsStopDateTime",
    "RootDirectoryCreateDate",
    "SMPTE12MUserDateTime",
    "SMPTE309MUserDateTime",
    "SampleDateTime",
    "ScanDate",
    "ScanSoftwareRevisionDate",
    "SeriesDateTime",
    "SettingDateTime",
    "ShotDate",
    "SigningDate",
    "SonyDateTime",
    "SonyDateTime2",
    "SourceDate",
    "SourceModified",
    "StartTime",
    "StartTimecode",
    "StartTimecodeRelativeToReference",
    "StorageFormatDate",
    "StorageFormatTime",
    "StudyDateTime",
    "SubSecCreateDate",
    "SubSecDateTimeOriginal",
    "SubSecModifyDate",
    "SubSecTime",
    "SubSecTimeDigitized",
    "SubSecTimeOriginal",
    "TaggingTime",
    "TemporalCoverageFrom",
    "TemporalCoverageTo",
    "ThumbnailDateTime",
    "Time",
    "Time1",
    "Time2",
    "TimeAndDate",
    "TimeCreated",
    "TimeSent",
    "TimeStamp",
    "TimeStamp1",
    "TimeStampList",
    "TimeZone",
    "TimeZone2",
    "TimeZoneCity",
    "TimeZoneCode",
    "TimeZoneDST",
    "TimeZoneInfo",
    "TimeZoneURL",
    "TimecodeCreationDateTime",
    "TimecodeEndDateTime",
    "TimecodeEventEndDateTime",
    "TimecodeEventStartDateTime",
    "TimecodeLastModifyDate",
    "TimecodeModifyDate",
    "TimecodeStartDateTime",
    "TimezoneID",
    "TimezoneName",
    "TimezoneOffsetFrom",
    "TimezoneOffsetTo",
    "TrackCreateDate",
    "TrackModifyDate",
    "TransformCreateDate",
    "TransformModifyDate",
    "UTCEndDateTime",
    "UTCEventEndDateTime",
    "UTCEventStartDateTime",
    "UTCInstantDateTime",
    "UTCLastModifyDate",
    "UTCStartDateTime",
    "UTCUserDateTime",
    "UnknownDate",
    "VersionCreateDate",
    "VersionModifyDate",
    "VersionsEventWhen",
    "VersionsModifyDate",
    "VideoModDate",
    "VolumeCreateDate",
    "VolumeEffectiveDate",
    "VolumeExpirationDate",
    "VolumeModifyDate",
    "WorldTimeLocation",
    "XAttrAppleMailDateReceived",
    "XAttrAppleMailDateSent",
    "XAttrLastUsedDate",
    "XAttrMDItemDownloadedDate",
    "Year",
    "YearCreated",
    "ZipModifyDate",
]

# These are the tags that I'm capturing with EXIFTool about creation time
DATE_TAGS_TO_CHECK: list[str] = [
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
OFFSET_DICT: dict[str, str] = {
    "ExifIFD:DateTimeOriginal": "ExifIFD:OffsetTimeOriginal",
    "ExifIFD:CreateDate": "ExifIFD:OffsetTimeDigitized",
    "ExifIFD:ModifyDate": "ExifIFD:OffsetTime",
}

# List of GPS tags to grab metadata from
GPS_TAGS_LIST: list[str] = [
    "GPSLatitudeRef",
    "GPSLatitude",
    "GPSLongitudeRef",
    "GPSLongitude",
]

# List of user comments tags, used to check iOS Screenshots
USER_COMMENTS_TAGS_LIST: list[str] = [
    "ExifIFD:UserComment",
    "XMP-exif:UserComment",
]
##
# Compiled Regexes
##

# GPS coordinates
GPSCoordsRegEx = compile(r"([0-9]+) deg ([0-9]+)' ([0-9.]+)\"")


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
    __slots__ = "fileName", "dateTime", "source", "sidecar", "EXIFTags", "newName"

    # NOTE: Tested
    def __init__(self, fileName: Path, dateTime: str | None, EXIFTags: dict[str, str] | None = None):
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
        newName: Path | None
            The proposed new name for the file, if we have all the info to process it, or None otherwise
        """
        self.fileName: Path = fileName
        # TODO: do some sort of datetime string validation here?
        self.dateTime: str | None = dateTime
        self.EXIFTags: dict[str, str] = EXIFTags or {}

        self.newName: Path | None = None
        self.sidecar: Path | None = self.findSidecar()
        self.source: str = self.getFileSource()

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
        dateTime_: str | None = cls._findCreationTime(etTagsDict)

        return cls(fileName=filename_, dateTime=dateTime_, EXIFTags=etTagsDict)

    @staticmethod
    # NOTE: Tested
    def _findCreationTime(exifToolData: dict[str, str]) -> str | None:
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

        # Loop through the DATE_TAGS_TO_CHECK tags. They are sorted by preference. As soon as we have one, we can take that one
        # as the date and break
        date: ZonedDateTime | OffsetDateTime | PlainDateTime | None = None
        for tag in DATE_TAGS_TO_CHECK:
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

                if not date:
                    break
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
                            int(longMatch.group(1))
                            + (int(longMatch.group(2)) / 60)
                            + (float(longMatch.group(3)) / 3600)
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
                    if tag in OFFSET_DICT.keys() and OFFSET_DICT[tag] in exifToolData.keys():
                        offsetStr = exifToolData[OFFSET_DICT[tag]]
                        if len(offsetStr) == 6:
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
                        elif offsetStr == "Z":
                            offsetTimeDelta = TimeDelta(hours=0)
                        else:
                            # Offset has to be ±HH:MM or 'Z'
                            raise ValueError(
                                f"In {exifToolData['SourceFile']}: Offset ('{offsetStr}') string has wrong length"
                            )
                        # Type dance: convert to plain (to get rid of whatever offset it had), assume it has a certain fixed
                        # offset, so we have a time with the same "value" but on a different offset.
                        date = date.to_plain().assume_fixed_offset(offsetTimeDelta)
                break

        if date:
            return date.format_common_iso()
        return None

    # NOTE: Tested
    def __repr__(self):
        """s
        Returns a string with the representation of the object: this string could be used to init an instance
        Example: MediaFile(fileName='Name', dateTime='1234-12-12 11-22-33+03:00', source="Apple iPhone 8")
        """
        return f"{type(self).__name__}(fileName=Path('{self.fileName}'), dateTime='{self.dateTime}', EXIFTags={self.EXIFTags})"

    def getNewName(self) -> None:
        self.newName = Path("")

    def hasMakeAndModel(self) -> str | None:
        """Checks the Make and Model tags to determine the source of the file

        Returns:
            str | None: a string with the source if it can be built from Make and Model tags, None otherwise
        """

        # Check 'IFD0' tags, the most frequently used, and if not present, 'Keys'
        make: str | None = None
        if "IFD0:Make" in self.EXIFTags.keys():
            make = self.EXIFTags["IFD0:Make"]
        elif "Keys:Make" in self.EXIFTags.keys():
            make = self.EXIFTags["Keys:Make"]

        model: str | None = None
        if "IFD0:Model" in self.EXIFTags.keys():
            model = self.EXIFTags["IFD0:Model"]
        elif "Keys:Model" in self.EXIFTags.keys():
            model = self.EXIFTags["Keys:Model"]

        if make and model:
            # Return make + model, except in some cases
            if make.lower() == "apple" or make.lower() == "google":
                # Remove "Apple" and "Google" from the source, just a preference
                return model
            elif make.lower() == "olympus imaging corp.":
                # That's just too long
                return "Olympus " + model
            elif make.lower() == "fujifilm":
                # It's odd to see Fuji as Fujifilm, remove the "film" bit
                return "Fuji " + model
            elif model.lower() == "oneplus a5010":
                # OnePlus adds the Make to the model, and uses the model number instead of the common name
                return make + "5T"
            elif make.lower() == "canon":
                # Canon adds "Canon" to the model too, so make + model is "Canon Canon"
                return model
            else:
                return make + " " + model

        return None

    def isScreenshot(self) -> str | None:
        """Checks the tags to determine if the MediaFile is a Screenshot. Only for iOS, Android screenshots don't have
        anything on them to identify them

        Returns:
            str | None: "Screenshot" if it's a iOS screenshot, None otherwise
        """

        for tag in USER_COMMENTS_TAGS_LIST:
            if tag in self.EXIFTags.keys():
                if self.EXIFTags[tag].lower() == "screenshot":
                    return "iOS Screenshot"
        return None

    def isInstragram(self) -> str | None:
        """Checks the tags to determine if the MediaFile comes from one of Meta's platforms (Instagram/Facebook)

        Returns:
            str | None: "Instagram" if it's a iOS screenshot, None otherwise
        """

        # If there's any key with partial match with "Software", the list comprehension
        # will not be empty
        softwareKeys = [key for key in self.EXIFTags.keys() if "software" in key.lower()]
        # Check for each key, while the flag is false, if the UserComment contains "facebook"
        # or "instagram"
        if softwareKeys != []:
            for key in softwareKeys:
                # stop stearching if one key with screenshot is found
                if "facebook" in self.EXIFTags[key].lower() or "instagram" in self.EXIFTags[key].lower():
                    return "Instagram"
        return None

    def isEditingSoftware(self) -> str | None:
        """Rule to apply "Photosho Etc." to all the files that don't match any other rule and have an Edition Software
        in the software tag (Photoshop, Lightroom, Gimp...)

        Returns:
            str | None: "Photoshop Etc." if the MediaFile matches the rule, None otherwise
        """
        # If there's any key with partial match with "Software", the list comprehension
        # will not be empty
        softwareKeys = [key for key in self.EXIFTags.keys() if "software" in key.lower()]
        # Check for each key, while the flag is false, if the UserComment contains "facebook"
        # or "instagram"
        if softwareKeys != []:
            for key in softwareKeys:
                # stop stearching if one key with screenshot is found
                if (
                    "photoshop" in self.EXIFTags[key].lower()
                    or "gimp" in self.EXIFTags[key].lower()
                    or "capture one" in self.EXIFTags[key].lower()
                ):
                    return "Photoshop Etc."
        return None

    # NOTE: Tested

    def isPicsArt(self) -> str | None:
        """
        Checks if a file comes from PicsArt

        Returns:
            str | None: "PicsArt" if it comes from PicsArt, None otherwise
        """

        if "IFD0:Software" in self.EXIFTags.keys() and self.EXIFTags["IFD0:Software"] == "PicsArt":
            return "PicsArt"

        return None

    def getFileSource(self) -> str:
        source = self.hasMakeAndModel()
        if not source:
            # If no make/model, check for screenshot
            source = self.isScreenshot()
        if not source:
            # Try now with Instagram pictures
            source = self.isInstragram()
        if not source:
            # Try now with PicsArt pictures
            source = self.isPicsArt()
        if not source:
            # Process files coming from Photoshop, as they are normally "more relevant" than simply WhatsApp images,
            # they come from "somewhere" more important and I think they deserve their own category. They normally
            # come from a Camera, and Photoshop respects the EXIF tags, so they are in all likelihood already sourced.
            # I leave this rule as the last, just before getting it in the WhatsApp bucket
            source = self.isEditingSoftware()
        if source:
            return source
        # Ultimately, if no other lead to get the source, asssume it's Whatsapp
        return "WhatsApp"

    def findSidecar(self) -> Path | None:
        """Finds if a file has a sidecar associated with it
        For an image with name pattern `name.ext`, sidecars have the name pattern of `name.aae`
        or `nameO.aae`

        Args:
            fileName (Path): a Path to the file to check for sidecars

        Returns:
            The path to a sidecar, if exists, or None if not found
        """
        fileName = self.fileName

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


###
# FILE MANIPULATION - Read from and write to file
###


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
def generateSortedMediaFileList(
    etData: list[dict[str, str]], itemProcessedCallBack: Callable[[], None] | None = None
) -> list[MediaFile]:
    """
    Creates a list of MediaFile objects from a list of dictionaries with tags comming from
    EXIFTool. The list is sorted by filename using natural sorting (as in "Windows Explorer Sorting")

    Args:
        etData (list[dict[str, str]): a list of dictionaries. Each dictionary is a collection of tags
        obtained from EXIFTool
        itemProcessedCallBack: Callable (() -> None ) | None. If passed, a callback to call on each item processed
        completion to indicate the progress.

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

        # If we passed a callback, call it to mark the item as processed, even for those not processable, as they are
        # in the list too (otherwise we would end up sort of item)
        if itemProcessedCallBack:
            itemProcessedCallBack()

    # Sorts the list based on the filename. This will help to infer dates based on
    # "neighbours" with date.
    mediaFileList = os_sorted(mediaFileList, key=lambda x: x.fileName)
    return mediaFileList


def getFilesInFolder(inputFolder: Path) -> int:
    """Gets the number of files that ExifTool can process in the folder RECUSIVELY

    Args:
        inputFolder (Path): folder to inspect

    Returns:
        int: total number of files that ExifTool can process
    """
    numFiles: int = 0
    cmdFind: list[str | Path] = ["exiftool", "-listdir", "-r", '"' + str(inputFolder) + '"']
    p = run(" ".join(cmdFind), stdout=PIPE, stderr=PIPE, shell=True, text=True)
    result = search("([0-9]*) image files read", p.stdout)
    if result:
        numFiles = int(result.group(1))
    else:
        module_logger.warning(f"Did not find files?\n\tCommand: {' '.join(str(x) for x in cmdFind)}\n\tOuput: {result}")
    return numFiles


# # NOTE: Tested
# def loadMediaFileListFromFile(inputFile: Path) -> list[MediaFile]:
#     """Loads and returns a list of MediaFile objects stored in a file passed as input

#     Args:
#         inputFile (Path): a file containing a list of MediaFile objects as text

#     Returns:
#         list[MediaFile]: a list of MediaFile objects
#     """
#     mediaFileList: list[MediaFile] = []
#     try:
#         with open(inputFile, "r") as readFile:
#             mediaFileData: str = readFile.read()
#     except FileNotFoundError:
#         module_logger.error(f"{inputFile} could not be found")
#         raise

#     try:
#         mediaFileList = eval(mediaFileData)
#     except SyntaxError:
#         module_logger.error(f"{inputFile} contents could not be eval()'ed")
#         raise

#     if not isinstance(mediaFileList[0], MediaFile):
#         raise TypeError(f"{inputFile} didn't contain a list of MediaFile")

#     return mediaFileList


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


# # NOTE: Tested
# def storeExifToolTags(outputFile: Path, listTags: list[dict[str, str]]) -> None:
#     """
#     Stores the list tags passed as parameter in the file specified

#     Args:
#         outputFile (Path): name of the file to store the data to.
#         listTags (list[dict[str,str]]): a list of dictionaries, containing the EXIF tags
#         as key-value pairs, from EXIFTool
#     """

#     with open(outputFile, "w") as writeFile:
#         writeFile.write(str(listTags))


####
# Creation date fixers
####


def isTagATimeTag(tag: str) -> bool:
    """Checks if the passed tag is one of the tags returned by -time:all

    Args:
        tag (str): the tag to check, as a string

    Returns:
        bool: true if it's in the -time:all shortcut, false otherwise
    """
    # Display data. We will filter the tags and display only the time-related ones. We have a list of time tags
    # but they don't have group info, so we have to split after the semicolon in order to match them
    # Split by the semicolon and take the second part
    if tag:
        tagGroup, separator, tagWithoutGroup = tag.partition(":")
        if separator:
            # If separator was found, the tag included group information
            if tagWithoutGroup in TIME_TAGS_LIST:
                return True
            # One Corner Case is that System File tags ("System:FileModifyDate", "System:FileAccessDate",
            # "System:FileCreateDate") are not in the list (as they might not be treated as EXIF tags)
            # Same for our "Inferred" dates
            if tagGroup == "System":
                return True
            elif tagGroup == "Inferred":
                return True
        else:
            # The tag might have been passed without a group, let's check it nevertheless
            if tag in TIME_TAGS_LIST:
                return True
    # Otherwise, it's not a time tag
    return False


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


# ### STEP 2 Process Data and Extract


def findNewNames(mediaFileList: list[MediaFile], parentFolder: Path) -> None:
    # Create a list of available sources
    availableSources = set([instance.source for instance in mediaFileList])

    for source in availableSources:
        # Date Histogram:
        # Find how many entries share the same date. We want to know this to figure out how many zeroes the file index will
        # have, so they are naturally sorted in the file explorer
        dateHistogram: dict[str, int] = Counter(
            OffsetDateTime.parse_common_iso(instance.dateTime).date().format_common_iso()
            for instance in mediaFileList
            if instance.source == source and instance.dateTime
        )

        # And to keep track of our progress, a dict with the same keys, but their values set to 0, and we will increase
        # them as we assign values to them
        dateHistogramLoop: dict[str, int] = dict.fromkeys(dateHistogram, 0)

        for mediaFile in mediaFileList:
            if mediaFile.source == source and mediaFile.dateTime:
                onlyDate: str = OffsetDateTime.parse_common_iso(mediaFile.dateTime).date().format_common_iso()
                # Name is "Date" + "Source" + "Number of file in that date" + "same file suffix"
                numberOfZeroes = len(str(dateHistogram[onlyDate]))
                dateHistogramLoop[onlyDate] += 1
                mediaFile.newName = Path(
                    parentFolder,
                    source
                    + "/"
                    + onlyDate
                    + " "
                    + mediaFile.source
                    + " "
                    + f"{dateHistogramLoop[onlyDate]:>0{numberOfZeroes}}"
                    + mediaFile.fileName.suffix,
                )


# def findNewNames(
#     mediaFileList: list[MediaFile],
#     photosDir: Path,
#     isDryRun: bool = False,
#     namePattern: str = "iPhone",
#     selectionSubfolder: str = "",
# ) -> None:
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
#     dateHistogram: dict[str, int] = Counter(instance.dateTime for instance in mediaFileList if instance.dateTime)

#     # Counter used to name the files, starts on 1, and increases for each file with the
#     # same capture date
#     # One for no
#     counter: int = 1
#     # String used to find when the date changes
#     prevDateStr: str = ""
#     for key in jsonData:
#         dateStr = jsonData[key]["date"]
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
#         renamedFile = (
#             photosDir
#             / selectionSubfolder
#             / f"{dateStr.replace(':', '-')} - {namePattern} {counter:>0{numberOfZeroes}}{currentFile.suffix}"
#         )


#         # Check if the file has a sidecar. They have the same filename than their parent file
#         # with .aae extension, but sometimes they have an 'O' at the end of the name ¯\_(ツ)_/¯
#         sidecarPath: Path = Path()
#         renamedSidecarPath = renamedFile.with_suffix(".aae")

#         # Print the name of the folder, if it's the first file in this folder we process
#         global oldDirectory
#         if currentFile.parent != oldDirectory:
#             module_logger.info(f"In {currentFile.parent}:")
#         oldDirectory = currentFile.parent  # and remember current folder for next run

#         if jsonData[key]["hasSidecar"]:
#             # Sometimes the sidecar has O at the end of the filename (most of the times), sometimes
#             # it doesn't. If the file with the O doesn't exist, try without it
#             sidecarPath = currentFile.parent / f"{currentFile.stem}O.aae"
#             if not sidecarPath.is_file():
#                 # module_logger.error("NO SIDECAR FOUND WITH O.aae, trying without O")
#                 sidecarPath = currentFile.parent / f"{currentFile.stem}.aae"
#                 if not sidecarPath.is_file():
#                     module_logger.error("NO SIDECAR FOUND WITH OR WITHOUT O.aae PATTERN")
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
#                 module_logger.info(f"Trying with sidecar {sidecarPath.name} for file {renamedFile.name}")
#                 sidecarPath.replace(renamedSidecarPath)
#         else:
#             # If dry-run is used, only print name changes
#             print(lvl.OK + f"File Name: {currentFile.name}\t->\t" + lvl.WARNING + f"{renamedFile.name}")
#             if jsonData[key]["hasSidecar"]:
#                 module_logger.error(f"\t And also rename sidecar {sidecarPath.name} to {renamedSidecarPath.name}")
#         prevDateStr = dateStr


# def generateMediaFileList(EXIFTagFile: Path) -> None:
#     # # Being quite explicit:
#     # # 1) read exif tags from file -> generate list of dicts
#     # exifDicts: list[dict[str, str]] = loadExifToolTagsFromFile(EXIFTagFile)
#     # # 2) Use list of dicts -> generate list of MediaFile
#     # mediaList: list[MediaFile] = generateSortedMediaFileList(exifDicts)
#     # print(mediaList)
#     # # 3) Store MediaFile list on disk
#     # storeMediaFileList(objectFile, mediaList)
#     # # 4) Find Dateless, try to correct them by hand
#     # dateless = [instance for instance in mediaList if instance.dateTime is None]
#     # print(dateless)
#     # print(f"Found {len(dateless)} {'instance' if (len(dateless) == 1) else 'instances'} without date")
#     # for item in dateless:
#     #     # find item in mediaList
#     #     idx = mediaList.index(item)
#     #     newDate = fixDateInteractive(idx, mediaList)
#     #     if newDate:
#     #         medialist[idx].dateTime = newDate

#     # storeMediaFileList(objectFile, mediaList)

#     return
