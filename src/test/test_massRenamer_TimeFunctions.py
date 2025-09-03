from pytest import fixture, raises
from exiftool import ExifToolHelper, ExifTool

from src.massRenamer.massRenamerClasses import findCreationTime, getTimeOffset, getTZAwareness, TZ_AWARENESS

"""
This file contains tests for all the time/date handling methods of the massRenamer module
"""

"""
getTimeOffset()

- Date is in CreateDate, there's a OffsetTimeDigitized tag, offset is added
- Date is in DateTimeOriginal tag, there's a OffsetTimeOriginal tag, offset is added
- Date is in any of the two tags, but there's no Offset tag, so consder UTC
- Date is in other tags, consider UTC
- String has no date, or incorrect date format
"""


def test_getTimeOffset_CreateDateWithOffsetTimeDigitized():
    assert (
        getTimeOffset(
            {"EXIF:CreateDate": "1234:12:23 01:02:03", "EXIF:OffsetTimeDigitized": "+02:00"}, "EXIF:CreateDate"
        )
        == "1234:12:23 01:02:03+02:00"
    )
    assert (
        getTimeOffset(
            {"EXIF:CreateDate": "1111:12:21 02:04:05", "EXIF:OffsetTimeDigitized": "-05:00"}, "EXIF:CreateDate"
        )
        == "1111:12:21 02:04:05-05:00"
    )
    assert (
        getTimeOffset({"EXIF:CreateDate": "1111:12:21 02:04:05", "EXIF:OffsetTimeDigitized": "Z"}, "EXIF:CreateDate")
        == "1111:12:21 02:04:05+00:00"
    )


def test_getTimeOffset_DateTimeOriginalWithOffsetTimeOriginal():
    assert (
        getTimeOffset(
            {"EXIF:DateTimeOriginal": "1234:12:23 01:02:03", "EXIF:OffsetTimeOriginal": "+02:00"},
            "EXIF:DateTimeOriginal",
        )
        == "1234:12:23 01:02:03+02:00"
    )
    assert (
        getTimeOffset(
            {"EXIF:DateTimeOriginal": "1111:12:21 02:04:05", "EXIF:OffsetTimeOriginal": "-05:00"},
            "EXIF:DateTimeOriginal",
        )
        == "1111:12:21 02:04:05-05:00"
    )
    assert (
        getTimeOffset(
            {"EXIF:DateTimeOriginal": "1111:12:21 02:04:05", "EXIF:OffsetTimeOriginal": "Z"}, "EXIF:DateTimeOriginal"
        )
        == "1111:12:21 02:04:05+00:00"
    )


def test_getTimeOffset_DateTimeTagWithoutOffsetInfo():
    assert getTimeOffset({"EXIF:CreateDate": "1111:12:21 02:04:05"}, "EXIF:CreateDate") == "1111:12:21 02:04:05+00:00"
    assert (
        getTimeOffset({"EXIF:DateTimeOriginal": "1234:12:23 01:02:03"}, "EXIF:DateTimeOriginal")
        == "1234:12:23 01:02:03+00:00"
    )


def test_getTimeOffset_OtherDateTags():
    assert getTimeOffset({"XMP:CreateDate": "1111:12:21 02:04:05"}, "XMP:CreateDate") == "1111:12:21 02:04:05+00:00"
    assert (
        getTimeOffset({"QuickTime:DateTimeOriginal": "1234:12:23 01:02:03"}, "QuickTime:DateTimeOriginal")
        == "1234:12:23 01:02:03+00:00"
    )


def test_getTimeOffset_NoDateTags():
    with raises(Exception) as e_info:
        getTimeOffset({"EXIF:Make": "Apple"}, "EXIF:Make")
    with raises(Exception) as e_info:
        getTimeOffset(
            {"QuickTime:DateTimeOriginal": "11:33:55 01:02:03"}, "QuickTime:DateTimeOriginal"
        ) == "1234:12:23 01:02:03+00:00"


"""
getTZAwareness()

- Date is TZ Aware
- Date is TZ Aware with Z
- Date is TZ Naive
- Date is not a Date
"""


def test_getTZAwareness_testAware():
    date: str = "1234:12:12 12:12:12+05:00"
    assert getTZAwareness(date) == TZ_AWARENESS.AWARE


def test_getTZAwareness_testAwareWithZ():
    date: str = "1234:12:12 12:12:12Z"
    assert getTZAwareness(date) == TZ_AWARENESS.Z_AWARE


def test_getTZAwareness_testNaive():
    date: str = "1234:12:12 12:12:12"
    assert getTZAwareness(date) == TZ_AWARENESS.NAIVE


def test_getTZAwareness_testNotADate():
    date: str = "1234:12:12 12:"
    assert getTZAwareness(date) == None


"""
findCreationTime()

- Success: file has EXIF:DateTimeOriginal, date string has offset
- Success: file has PGN:CreateDate, date string does has offset
- Success: file has EXIF:DateTimeOriginal, date has no offset but there's an offset tag
- Success: file has EXIF:DateTimeOriginal, date has no offset or offset tag, but we have lat/long
- Partial success: file has EXIF:DateTimeOriginal, unable to determine offset
- Worst scenario: unable to get a time on it.
"""


hasDateTimeOriginalWithOffsetDict: dict[str, str] = {
    "ExifIFD:DateTimeOriginal": "2025-01-01T10:48:44+00:00",
    "ExifIFD:CreateDate": "2025-01-02T11:00:00+01:00",
}


def test_findCreationTime_hasDateTimeOriginalWithOffset():
    ### Prepare the test
    expectedDateTimeStr = "2025-01-01T10:48:44+00:00"

    ### Execute
    date = findCreationTime(hasDateTimeOriginalWithOffsetDict)

    ### Assert
    assert expectedDateTimeStr == date
    # Check that DateTimeOriginal has precedence over CreateDAte
    assert "2025-01-02T11:00:00+01:00" != date


PNGCreationDateDict: dict[str, str] = {
    "XMP-photoshop:DateCreated": "2025-01-01T00:45:59+00:00",
}


def test_findCreationTime_hasPNGDate():
    ### Prepare the test
    expectedDateTimeStr = "2025-01-01T00:45:59+00:00"

    ### Execute
    date = findCreationTime(PNGCreationDateDict)

    ### Assert
    assert expectedDateTimeStr == date


offsetInItsOwnTag: dict[str, str] = {
    "ExifIFD:DateTimeOriginal": "2025-01-01T10:48:44+00:00",
    "ExifIFD:OffsetTimeOriginal": "+01:00",  # <- correct offset for DateTimeOriginal
    "ExifIFD:OffsetTime": "+02:00",
    "ExifIFD:OffsetTimeDigitized": "+03:00",
}

offsetInItsOwnTag2: dict[str, str] = {
    "ExifIFD:CreateDate": "2025-01-01T10:48:44-05:00",
    "ExifIFD:OffsetTimeOriginal": "+01:00",
    "ExifIFD:OffsetTime": "+02:00",
    "ExifIFD:OffsetTimeDigitized": "-03:30",  # <- correct offset for CreateDate
}

noOffsetInTagButHasOffsetTag: dict[str, str] = {
    "ExifIFD:CreateDate": "2025-01-01T10:48:44",
    "ExifIFD:OffsetTimeDigitized": "+02:00",  # <- correct offset for CreateDate
}


def test_findCreationTime_hasOffsetInAnotherTag():
    ### Prepare the test
    expectedDateTimeStr = "2025-01-01T10:48:44+01:00"

    ### Execute
    date = findCreationTime(offsetInItsOwnTag)

    ### Assert
    assert expectedDateTimeStr == date

    ### Second Test, with a different set of date tags (createDate), plus negative offset and minutes in offset
    expectedDateTimeStr2 = "2025-01-01T10:48:44-03:30"

    ### Execute
    date2 = findCreationTime(offsetInItsOwnTag2)

    ### Assert
    assert expectedDateTimeStr2 == date2

    ### Third Test, no offset in date tag, but has offset tag!
    expectedDateTimeStr3 = "2025-01-01T10:48:44+02:00"

    ### Execute
    date3 = findCreationTime(noOffsetInTagButHasOffsetTag)

    ### Assert
    assert expectedDateTimeStr3 == date3


noOffset: dict[str, str] = {
    "ExifIFD:DateTimeOriginal": "2025-01-01T10:48:44",
}


def test_findCreationTime_noOffset_ConsiderUTC():
    ### Prepare the test
    expectedDateTimeStr = "2025-01-01T10:48:44+00:00"

    ### Execute
    date = findCreationTime(noOffset)

    ### Assert
    assert expectedDateTimeStr == date


noDates: dict[str, str] = {
    "Keys:CreationDate": "2025-01-03T16:58:21+00:00",
    "Keys:Make": "Apple",
    "Keys:Model": "iPhone 13 mini",
    "Keys:Software": "17.6.1",
}


def test_findCreationDate_noDates():
    ### Prepare the test
    expectedDateTimeStr = None

    ### Execute
    date = findCreationTime(noDates)

    ### Assert
    assert expectedDateTimeStr == date


# No Offset, but GPS coordinates
GPSCoordinatesDict: dict[str, str] = {
    "ExifIFD:DateTimeOriginal": "2025-01-01T10:48:44",
    "GPS:GPSLatitudeRef": "North",
    "GPS:GPSLatitude": "42 deg 3' 45.27\"",
    "GPS:GPSLongitudeRef": "West",
    "GPS:GPSLongitude": "1 deg 36' 46.65\"",
}


def test_findCreationTime_GPSCoordinates():
    ### Prepare the test
    # 10:48 UTC with Europe/Madrid coordinates is 11:41+001:00
    expectedDateTimeStr = "2025-01-01T11:48:44+01:00"

    ### Execute
    date = findCreationTime(GPSCoordinatesDict)

    ### Assert
    assert expectedDateTimeStr == date


# No Offset, but GPS coordinates this time South West (so both negative)
GPSCoordinatesSouthWestDict: dict[str, str] = {
    "ExifIFD:DateTimeOriginal": "2025-01-01T10:48:44",
    "GPS:GPSLatitudeRef": "South",
    "GPS:GPSLatitude": "22 deg 3' 45.27\"",
    "GPS:GPSLongitudeRef": "West",
    "GPS:GPSLongitude": "54 deg 36' 46.65\"",
}


def test_findCreationTime_GPSCoordinatesSouthWest():
    ### Prepare the test
    # 10:48 UTC with Brasil/Sao Paulo coordinates is 06:41-04:00
    expectedDateTimeStr = "2025-01-01T06:48:44-04:00"

    ### Execute
    date = findCreationTime(GPSCoordinatesSouthWestDict)

    ### Assert
    assert expectedDateTimeStr == date


# GPS coordinates, so we must ignore offsets
GPSCoordinatesIgnoreOffsetDict: dict[str, str] = {
    "ExifIFD:DateTimeOriginal": "2025-01-01T10:48:44+00:00",  # wrong offset
    "ExifIFD:OffsetTimeOriginal": "+05:00",  # wrong offset
    "GPS:GPSLatitudeRef": "North",  # should return +1
    "GPS:GPSLatitude": "42 deg 3' 45.27\"",
    "GPS:GPSLongitudeRef": "West",
    "GPS:GPSLongitude": "1 deg 36' 46.65\"",
}


def test_findCreationTime_GPSCoordinatesIgnoreOffset():
    ### Prepare the test
    # 10:48 UTC with Europe/Madrid coordinates is 11:41+001:00
    expectedDateTimeStr = "2025-01-01T11:48:44+01:00"

    ### Execute
    date = findCreationTime(GPSCoordinatesIgnoreOffsetDict)

    ### Assert
    assert expectedDateTimeStr == date


"""
inferDateFromNeighbours

- Get the date from the previous item

"""


# @fixture
# def listPhotoOneDatelessTest1():
#     exifData0 = {
#         "SourceFile": "fakeFile1.jpg",
#         "EXIF:Make": "Apple",
#         "EXIF:Model": "iPhone 8",
#         "EXIF:CreateDate": "1234:12:12 11:22:33",
#     }
#     exifData1 = {"SourceFile": "fakeFile2.jpg", "EXIF:Make": "Apple", "EXIF:Model": "iPhone 8"}
#     exifData2 = {
#         "SourceFile": "fakeFile3.jpg",
#         "EXIF:Make": "Apple",
#         "EXIF:Model": "iPhone 8",
#         "EXIF:CreateDate": "1234:12:12 11:30:33",
#     }
#     return [MediaFile.fromExifTags(exifData0), MediaFile.fromExifTags(exifData1), MediaFile.fromExifTags(exifData2)]


# def test_inferDateFromNeighboursTest1(listPhotoOneDatelessTest1):
#     listOfItems: List[MediaFile] = listPhotoOneDatelessTest1
#     assert inferDateFromNeighbours(1, listOfItems) == "1234:12:12 11:29:33+00:00"


# @fixture
# def listPhotoOneDatelessTest2():
#     exifData0 = {"SourceFile": "fakeFile1.jpg", "EXIF:Make": "Apple", "EXIF:Model": "iPhone 8"}
#     exifData1 = {"SourceFile": "fakeFile2.jpg", "EXIF:Make": "Apple", "EXIF:Model": "iPhone 8"}
#     exifData2 = {
#         "SourceFile": "fakeFile3.jpg",
#         "EXIF:Make": "Apple",
#         "EXIF:Model": "iPhone 8",
#         "EXIF:CreateDate": "1234:12:12 11:30:33",
#     }
#     return [MediaFile.fromExifTags(exifData0), MediaFile.fromExifTags(exifData1), MediaFile.fromExifTags(exifData2)]


# def test_inferDateFromNeighboursTest2(listPhotoOneDatelessTest2):
#     listOfItems: List[MediaFile] = listPhotoOneDatelessTest2
#     assert inferDateFromNeighbours(1, listOfItems) == "1234:12:12 11:29:33+00:00"


# @fixture
# def listPhotoOneDatelessPreviousTest3():
#     photoList = [
#         {
#             "SourceFile": "fakeFile1.jpg",
#             "EXIF:Make": "Apple",
#             "EXIF:Model": "iPhone 8",
#             "EXIF:CreateDate": "1234:12:12 11:22:33",
#         },
#         {
#             "SourceFile": "fakeFile3.jpg",
#             "EXIF:Make": "Apple",
#             "EXIF:Model": "iPhone 8",
#             "EXIF:CreateDate": "1234:12:12 11:30:33",
#         },
#         {"SourceFile": "fakeFile1.jpg", "EXIF:Make": "Apple", "EXIF:Model": "iPhone 8"},
#         {"SourceFile": "fakeFile2.jpg", "EXIF:Make": "Apple", "EXIF:Model": "iPhone 8"},
#         {
#             "SourceFile": "fakeFile3.jpg",
#             "EXIF:Make": "Apple",
#             "EXIF:Model": "iPhone 8",
#             "EXIF:CreateDate": "1234:12:12 11:40:33",
#         },
#     ]
#     return [MediaFile.fromExifTags(photo) for photo in photoList]


# def test_inferDateFromNeighboursTest3(listPhotoOneDatelessPreviousTest3):
#     listOfItems: List[MediaFile] = listPhotoOneDatelessPreviousTest3
#     assert inferDateFromNeighbours(3, listOfItems) == "1234:12:12 11:32:33+00:00"


# @fixture
# def listPhotoOneDatelessPreviousTest4():
#     photoList = [
#         {"SourceFile": "fakeFile1.jpg", "EXIF:Make": "Apple", "EXIF:Model": "iPhone 8"},
#         {"SourceFile": "fakeFile3.jpg", "EXIF:Make": "Apple", "EXIF:Model": "iPhone 8"},
#         {"SourceFile": "fakeFile1.jpg", "EXIF:Make": "Apple", "EXIF:Model": "iPhone 8"},
#         {"SourceFile": "fakeFile2.jpg", "EXIF:Make": "Apple", "EXIF:Model": "iPhone 8"},
#         {
#             "SourceFile": "fakeFile3.jpg",
#             "EXIF:Make": "Apple",
#             "EXIF:Model": "iPhone 8",
#             "EXIF:CreateDate": "1234:12:12 11:40:33",
#         },
#     ]
#     return [MediaFile.fromExifTags(photo) for photo in photoList]


# def test_inferDateFromNeighboursTest4(listPhotoOneDatelessPreviousTest4):
#     listOfItems: List[MediaFile] = listPhotoOneDatelessPreviousTest4
#     assert inferDateFromNeighbours(2, listOfItems) == "1234:12:12 11:38:33+00:00"


# @fixture
# def listPhotoOneDatelessPreviousTest5():
#     photoList = [
#         {"SourceFile": "fakeFile1.jpg", "EXIF:Make": "Apple", "EXIF:Model": "iPhone 8"},
#         {"SourceFile": "fakeFile3.jpg", "EXIF:Make": "Apple", "EXIF:Model": "iPhone 8"},
#         {"SourceFile": "fakeFile1.jpg", "EXIF:Make": "Apple", "EXIF:Model": "iPhone 8"},
#         {"SourceFile": "fakeFile2.jpg", "EXIF:Make": "Apple", "EXIF:Model": "iPhone 8"},
#         {"SourceFile": "fakeFile3.jpg", "EXIF:Make": "Apple", "EXIF:Model": "iPhone 8"},
#     ]
#     return [MediaFile.fromExifTags(photo) for photo in photoList]


# def test_inferDateFromNeighboursTest5(listPhotoOneDatelessPreviousTest5):
#     listOfItems: List[MediaFile] = listPhotoOneDatelessPreviousTest5
#     assert inferDateFromNeighbours(2, listOfItems) == None


# def test_fixDateInteractive_Success(listPhotoOneDatelessPreviousTest3, mocker):
#     listOfItems: List[MediaFile] = listPhotoOneDatelessPreviousTest3
#     datelessItem = 2
#     fileName = listOfItems[datelessItem].getFileName()
#     resonse: str = (
#         "[File]          FileInodeChangeDate             : 2024:03:13 14:22:20+00:00\n"
#         "[QuickTime]     CreateDate                      : 2018:02:28 02:25:37\n"
#         "[QuickTime]     ModifyDate                      : 2018:02:28 02:25:39\n"
#         "[QuickTime]     TrackCreateDate                 : 2018:02:28 02:25:37\n"
#         "[QuickTime]     TrackModifyDate                 : 2018:02:28 02:25:39\n"
#         "[QuickTime]     MediaCreateDate                 : 2018:02:28 02:25:37\n"
#         "[QuickTime]     MediaModifyDate                 : 2018:02:28 02:25:39"
#     )
#     mocker.patch("exiftool.ExifTool.execute", return_value=resonse)
#     mocker.patch("massRenamer.massRenamerClasses._getInput", return_value="2")

#     assert fixDateInteractive(datelessItem, listOfItems) == "2018:02:28 02:25:37"
#     ExifTool.execute.assert_called_with("-time:all", "-G1", "-a", "-s", str(fileName))


# def test_fixDateInteractive_CantParseTime(listPhotoOneDatelessPreviousTest3, mocker):
#     listOfItems: List[MediaFile] = listPhotoOneDatelessPreviousTest3
#     datelessItem = 2
#     fileName = listOfItems[datelessItem].getFileName()
#     resonse: str = (
#         "[File]          FileInodeChangeDate             : 2024:03:13 14:22:20+00:00\n"
#         "[QuickTime]     CreateDate                      : AAAA:BB:CC 02:25:37\n"
#         "[QuickTime]     ModifyDate                      : 2018:02:28 02:25:39\n"
#         "[QuickTime]     TrackCreateDate                 : 2018:02:28 02:25:37\n"
#         "[QuickTime]     TrackModifyDate                 : 2018:02:28 02:25:39\n"
#         "[QuickTime]     MediaCreateDate                 : 2018:02:28 02:25:37\n"
#         "[QuickTime]     MediaModifyDate                 : 2018:02:28 02:25:39"
#     )
#     mocker.patch("exiftool.ExifTool.execute", return_value=resonse)
#     mocker.patch("massRenamer.massRenamerClasses._getInput", return_value="2")

#     assert fixDateInteractive(datelessItem, listOfItems) == None
#     ExifTool.execute.assert_called_with("-time:all", "-G1", "-a", "-s", str(fileName))


# def test_fixDateInteractive_SaveProgressToDisk(listPhotoOneDatelessPreviousTest3, mocker):
#     listOfItems: List[MediaFile] = listPhotoOneDatelessPreviousTest3
#     datelessItem = 2
#     fileName = listOfItems[datelessItem].getFileName()
#     resonse: str = (
#         "[File]          FileInodeChangeDate             : 2024:03:13 14:22:20+00:00\n"
#         "[QuickTime]     CreateDate                      : AAAA:BB:CC 02:25:37\n"
#         "[QuickTime]     ModifyDate                      : 2018:02:28 02:25:39\n"
#         "[QuickTime]     TrackCreateDate                 : 2018:02:28 02:25:37\n"
#         "[QuickTime]     TrackModifyDate                 : 2018:02:28 02:25:39\n"
#         "[QuickTime]     MediaCreateDate                 : 2018:02:28 02:25:37\n"
#         "[QuickTime]     MediaModifyDate                 : 2018:02:28 02:25:39"
#     )

#     # Mock a file being opened, return the "open" object on m
#     m = mocker.patch("massRenamer.massRenamerClasses.open", mocker.mock_open())
#     mocker.patch("exiftool.ExifTool.execute", return_value=resonse)
#     mocker.patch("massRenamer.massRenamerClasses._getInput", return_value="-1")
#     # mocker.patch("massRenamer.massRenamerClasses.storeMediaFileList")
#     with raises(SystemExit) as pytest_wrapped_e:
#         fixDateInteractive(datelessItem, listOfItems)
#     assert pytest_wrapped_e.type == SystemExit
#     assert pytest_wrapped_e.value.code == 0
#     # check that open was called with a Path and the 'w' mode
#     m.assert_called_once_with(Path("MediaFileList.txt"), "w")
#     # And now, check it was written: notice that now we don't use m.write, but m().write!
#     m().write.assert_called_once_with(str(listOfItems))
#     ExifTool.execute.assert_called_with("-time:all", "-G1", "-a", "-s", str(fileName))


# def test_fixDateInteractive_SkipFile(listPhotoOneDatelessPreviousTest3, mocker):
#     listOfItems: List[MediaFile] = listPhotoOneDatelessPreviousTest3
#     datelessItem = 2
#     fileName = listOfItems[datelessItem].getFileName()
#     resonse: str = (
#         "[File]          FileInodeChangeDate             : 2024:03:13 14:22:20+00:00\n"
#         "[QuickTime]     CreateDate                      : AAAA:BB:CC 02:25:37\n"
#         "[QuickTime]     ModifyDate                      : 2018:02:28 02:25:39\n"
#         "[QuickTime]     TrackCreateDate                 : 2018:02:28 02:25:37\n"
#         "[QuickTime]     TrackModifyDate                 : 2018:02:28 02:25:39\n"
#         "[QuickTime]     MediaCreateDate                 : 2018:02:28 02:25:37\n"
#         "[QuickTime]     MediaModifyDate                 : 2018:02:28 02:25:39"
#     )
#     mocker.patch("exiftool.ExifTool.execute", return_value=resonse)
#     mocker.patch("massRenamer.massRenamerClasses._getInput", return_value="0")

#     assert fixDateInteractive(datelessItem, listOfItems) == None
#     ExifTool.execute.assert_called_with("-time:all", "-G1", "-a", "-s", str(fileName))


# def test_fixDateInteractive_WeirdInput(listPhotoOneDatelessPreviousTest3, mocker):
#     listOfItems: List[MediaFile] = listPhotoOneDatelessPreviousTest3
#     datelessItem = 2
#     fileName = listOfItems[datelessItem].getFileName()
#     resonse: str = (
#         "[File]          FileInodeChangeDate             : 2024:03:13 14:22:20+00:00\n"
#         "[QuickTime]     CreateDate                      : AAAA:BB:CC 02:25:37\n"
#         "[QuickTime]     ModifyDate                      : 2018:02:28 02:25:39\n"
#         "[QuickTime]     TrackCreateDate                 : 2018:02:28 02:25:37\n"
#         "[QuickTime]     TrackModifyDate                 : 2018:02:28 02:25:39\n"
#         "[QuickTime]     MediaCreateDate                 : 2018:02:28 02:25:37\n"
#         "[QuickTime]     MediaModifyDate                 : 2018:02:28 02:25:39"
#     )
#     mocker.patch("exiftool.ExifTool.execute", return_value=resonse)
#     mocker.patch("massRenamer.massRenamerClasses._getInput", return_value="A")

#     assert fixDateInteractive(datelessItem, listOfItems) == None
#     ExifTool.execute.assert_called_with("-time:all", "-G1", "-a", "-s", str(fileName))
