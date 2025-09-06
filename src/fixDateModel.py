from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex, QPersistentModelIndex
from PySide6.QtGui import QColor, QFont

# These are all the time tags that -time:all extract. Note that these tags don't have their group attached to them
# Extracted with exiftool -list -time:all
TIME_TAGS_LIST: list[str] = [
    "ABDate",
    "AccessDate",
    "Acknowledged",
    "AcquisitionTime",
    "AcquisitionTimeDayAcquisitionTimeMonth",
    "AcquisitionTimeStamp",
    "AcquisitionTimeYearAcquisitionTimeYearMonth",
    "AcquisitionTimeYearMonthDay",
    "AppleMailDateReceivedAppleMailDateSent",
    "ArtworkCircaDateCreated",
    "ArtworkDateCreated",
    "AudioModDateBackupTime",
    "Birthday",
    "BroadcastDate",
    "BroadcastTime",
    "BuildDate",
    "CFEGFlashTimeStampCalibrationDateTime",
    "CameraDateTime",
    "CameraPoseTimestamp",
    "CaptionsDateTimeStampsCircaDateCreated",
    "ClassifyingCountryCodingMethodDate",
    "ClipCreationDateTimeCommentTime",
    "ContainerLastModifyDate",
    "ContentCreateDate",
    "ContractDateTimeCopyrightYear",
    "CoverDate",
    "CreateDate",
    "CreationDate",
    "CreationTime",
    "DataCreateDateDataModifyDate",
    "Date",
    "Date1",
    "Date2",
    "DateAccessed",
    "DateAcquired",
    "DateArchivedDateCompleted",
    "DateCreated",
    "DateDisplayFormat",
    "DateEncoded",
    "DateIdentifiedDateImported",
    "DateLastSaved",
    "DateModified",
    "DatePictureTaken",
    "DatePurchasedDateReceived",
    "DateRecieved",
    "DateReleased",
    "DateSent",
    "DateTagged",
    "DateTime",
    "DateTime1DateTime2",
    "DateTimeCompleted",
    "DateTimeCreated",
    "DateTimeDigitizedDateTimeDropFrameFlag",
    "DateTimeDue",
    "DateTimeEmbeddedFlag",
    "DateTimeEndDateTimeGenerated",
    "DateTimeKind",
    "DateTimeOriginal",
    "DateTimeRate",
    "DateTimeStampDateTimeStart",
    "DateTimeUTC",
    "DateVisited",
    "DateWritten",
    "DayOfWeek",
    "DaylightSavingsDeclassificationDate",
    "DeprecatedOn",
    "DerivedFromLastModifyDate",
    "DestinationCityDestinationDST",
    "DigitalCreationDate",
    "DigitalCreationDateTimeDigitalCreationTime",
    "EarthPosTimestamp",
    "EmbargoDate",
    "EncodeTime",
    "EncodingTimeEndTime",
    "EventAbsoluteDuration",
    "EventDate",
    "EventDay",
    "EventEarliestDateEventEndDayOfYear",
    "EventEndTimecodeOffset",
    "EventLatestDate",
    "EventMonthEventStartDayOfYear",
    "EventStartTime",
    "EventStartTimecodeOffset",
    "EventTimeEventVerbatimEventDate",
    "EventYear",
    "ExceptionDateTimes",
    "ExclusivityEndDateExpirationDate",
    "ExpirationTime",
    "ExtensionCreateDate",
    "ExtensionModifyDateFileAccessDate",
    "FileCreateDate",
    "FileInodeChangeDate",
    "FileModifyDateFilmTestResult",
    "FirstPhotoDate",
    "FirstPublicationDate",
    "FormatVersionTimeGPSDateStamp",
    "GPSDateTime",
    "GPSDateTimeRaw",
    "GPSTimeStamp",
    "HistoryWhen",
    "HometownCityHometownDST",
    "HumanObservationDay",
    "HumanObservationEarliestDateHumanObservationEndDayOfYear",
    "HumanObservationEventDateHumanObservationEventTime",
    "HumanObservationLatestDate",
    "HumanObservationMonthHumanObservationStartDayOfYear",
    "HumanObservationVerbatimEventDateHumanObservationYear",
    "IPTCLastEdited",
    "ImageProcessingFileDateCreatedIngredientsLastModifyDate",
    "KillDateDate",
    "LastBackupDate",
    "LastPhotoDateLastPrinted",
    "LastUpdate",
    "LayerModifyDates",
    "LicenseEndDate",
    "LicenseStartDateLicenseTransactionDate",
    "LocalCreationDateTime",
    "LocalEndDateTimeLocalEventEndDateTime",
    "LocalEventStartDateTime",
    "LocalFestivalDateTimeLocalLastModifyDate",
    "LocalModifyDate",
    "LocalStartDateTime",
    "LocalUserDateTimeLocationDate",
    "MDItemContentCreationDate",
    "MDItemContentCreationDateRankingMDItemContentCreationDate_Ranking",
    "MDItemContentModificationDateMDItemDateAdded",
    "MDItemDateAdded_Ranking",
    "MDItemDownloadedDateMDItemFSContentChangeDate",
    "MDItemFSCreationDate",
    "MDItemGPSDateStampMDItemInterestingDateRanking",
    "MDItemInterestingDate_Ranking",
    "MDItemLastUsedDateMDItemMailDateReceived_Ranking",
    "MDItemTimestamp",
    "MDItemUsedDatesMDItemUserDownloadedDate",
    "MachineObservationDay",
    "MachineObservationEarliestDateMachineObservationEndDayOfYear",
    "MachineObservationEventDateMachineObservationEventTime",
    "MachineObservationLatestDateMachineObservationMonth",
    "MachineObservationStartDayOfYearMachineObservationVerbatimEventDate",
    "MachineObservationYearManagedFromLastModifyDate",
    "ManifestReferenceLastModifyDate",
    "ManufactureDateManufactureDate1",
    "ManufactureDate2",
    "MaterialAbsoluteDurationMaterialEndTimecodeOffset",
    "MeasurementDeterminedDate",
    "MediaCreateDateMediaModifyDate",
    "MediaOriginalBroadcastDateTime",
    "MetadataDateMetadataLastEdited",
    "MetadataModDate",
    "MinoltaDate",
    "MinoltaTime",
    "ModDateModificationDate",
    "ModifyDate",
    "Month",
    "MonthDayCreated",
    "MoonPhase",
    "NikonDateTime",
    "NowON1_SettingsMetadataCreated",
    "ON1_SettingsMetadataModifiedON1_SettingsMetadataTimestamp",
    "ObjectCountryCodingMethodDate",
    "ObservationDateObservationDateEnd",
    "ObservationTime",
    "ObservationTimeEnd",
    "OffSaleDateDateOffsetTime",
    "OffsetTimeDigitized",
    "OffsetTimeOriginal",
    "OnSaleDateDateOptionEndDate",
    "OriginalCreateDateTime",
    "OriginalReleaseTime",
    "OriginalReleaseYearOtherDate1",
    "OtherDate2",
    "OtherDate3",
    "PDBCreateDate",
    "PDBModifyDatePackageLastModifyDate",
    "PanasonicDateTime",
    "PatientBirthDate",
    "PaymentDueDateTimePhysicalMediaLength",
    "PlanePoseTimestamp",
    "PoseTimestamp",
    "PowerUpTime",
    "PreviewDatePreviewDateTime",
    "ProducedDate",
    "ProductionDate",
    "ProfileDateTimePublicationDateDate",
    "PublicationDisplayDateDate",
    "PublicationEventDatePublishDate",
    "PublishDateStart",
    "RecordedDate",
    "RecordingTime",
    "RecordingTimeDayRecordingTimeMonth",
    "RecordingTimeYear",
    "RecordingTimeYearMonthRecordingTimeYearMonthDay",
    "RecurrenceDateTimes",
    "RecurrenceRule",
    "ReelTimecodeReferenceDate",
    "RegionInfoDateRegionsValid",
    "RegisterCreationTimeRegisterItemStatusChangeDateTime",
    "RegisterReleaseDateTime",
    "RegisterUserTimeRelationshipEstablishedDate",
    "ReleaseDate",
    "ReleaseDateDay",
    "ReleaseDateMonthReleaseDateYear",
    "ReleaseDateYearMonth",
    "ReleaseDateYearMonthDay",
    "ReleaseTimeRenditionOfLastModifyDate",
    "RevisionDate",
    "RicohDate",
    "RightsStartDateTimeRightsStopDateTime",
    "RootDirectoryCreateDate",
    "SMPTE12MUserDateTimeSMPTE309MUserDateTime",
    "SampleDateTime",
    "ScanDate",
    "ScanSoftwareRevisionDateSeriesDateTime",
    "SettingDateTime",
    "ShotDate",
    "SigningDate",
    "SonyDateTimeSonyDateTime2",
    "SourceDate",
    "SourceModified",
    "StartTime",
    "StartTimecodeStartTimecodeRelativeToReference",
    "StorageFormatDate",
    "StorageFormatTimeStudyDateTime",
    "SubSecCreateDate",
    "SubSecDateTimeOriginal",
    "SubSecModifyDateSubSecTime",
    "SubSecTimeDigitized",
    "SubSecTimeOriginal",
    "TaggingTimeTemporalCoverageFrom",
    "TemporalCoverageTo",
    "ThumbnailDateTime",
    "Time",
    "Time1",
    "Time2TimeAndDate",
    "TimeCreated",
    "TimeSent",
    "TimeStamp",
    "TimeStamp1",
    "TimeStampList",
    "TimeZoneTimeZone2",
    "TimeZoneCity",
    "TimeZoneCode",
    "TimeZoneDST",
    "TimeZoneInfo",
    "TimeZoneURLTimecodeCreationDateTime",
    "TimecodeEndDateTime",
    "TimecodeEventEndDateTimeTimecodeEventStartDateTime",
    "TimecodeLastModifyDate",
    "TimecodeModifyDateTimecodeStartDateTime",
    "TimezoneID",
    "TimezoneName",
    "TimezoneOffsetFromTimezoneOffsetTo",
    "TrackCreateDate",
    "TrackModifyDate",
    "TransformCreateDateTransformModifyDate",
    "UTCEndDateTime",
    "UTCEventEndDateTime",
    "UTCEventStartDateTimeUTCInstantDateTime",
    "UTCLastModifyDate",
    "UTCStartDateTime",
    "UTCUserDateTimeUnknownDate",
    "VersionCreateDate",
    "VersionModifyDate",
    "VersionsEventWhenVersionsModifyDate",
    "VideoModDate",
    "VolumeCreateDate",
    "VolumeEffectiveDateVolumeExpirationDate",
    "VolumeModifyDate",
    "WorldTimeLocationXAttrAppleMailDateReceived",
    "XAttrAppleMailDateSent",
    "XAttrLastUsedDateXAttrMDItemDownloadedDate",
    "Year",
    "YearCreated",
    "ZipModifyDate",
]


class fixDateModel(QAbstractTableModel):
    # Sunny Beach Day Palette
    blue = "#70a7bd"
    teal = "#7bdcd0"
    yellow = "#f3dfaf"
    orange = "#f9cdaa"
    darkOrange = "#f2b2a2"

    def __init__(self, dateTagList: list[tuple[str, str]] | None = None) -> None:
        super().__init__()
        self.dateTagList = dateTagList or []

    def data(
        self, index: QModelIndex | QPersistentModelIndex, role: int = Qt.ItemDataRole.DisplayRole
    ) -> str | QColor | QFont | None:
        if role == Qt.ItemDataRole.DisplayRole:
            return self.dateTagList[index.row()][index.column()]
        elif role == Qt.ItemDataRole.BackgroundRole:
            # Get some background colours to distinghuis tags?
            if self.dateTagList[index.row()][0].startswith("System"):
                return QColor(self.darkOrange)
            if self.dateTagList[index.row()][0].startswith("Exif"):
                return QColor(self.orange)
            if self.dateTagList[index.row()][0].startswith("Inferred"):
                return QColor(self.yellow)
            else:
                return QColor(self.teal)
        elif role == Qt.ItemDataRole.FontRole and index.column() == 1:
            myFont = QFont("Monospace")
            return myFont
        return None

    def rowCount(self, parent: QModelIndex | QPersistentModelIndex = QModelIndex()) -> int:
        return len(self.dateTagList)

    def columnCount(self, parent: QModelIndex | QPersistentModelIndex = QModelIndex()) -> int:
        return 2

    def replaceListOfTags(self, newDateTagList: list[tuple[str, str]]) -> None:
        self.dateTagList = newDateTagList
        self.layoutChanged.emit()


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
