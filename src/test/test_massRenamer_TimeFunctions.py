from pytest import raises

from src.massRenamer.massRenamerClasses import MediaFile, inferDateFromNeighbours

"""
This file contains tests for all the time/date handling methods of the massRenamer module
"""

"""
MediaFile._findCreationTime()

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
    date = MediaFile._findCreationTime(hasDateTimeOriginalWithOffsetDict)  # pyright: ignore[reportPrivateUsage]

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
    date = MediaFile._findCreationTime(PNGCreationDateDict)  # pyright: ignore[reportPrivateUsage]

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
    date = MediaFile._findCreationTime(offsetInItsOwnTag)  # pyright: ignore[reportPrivateUsage]

    ### Assert
    assert expectedDateTimeStr == date

    ### Second Test, with a different set of date tags (createDate), plus negative offset and minutes in offset
    expectedDateTimeStr2 = "2025-01-01T10:48:44-03:30"

    ### Execute
    date2 = MediaFile._findCreationTime(offsetInItsOwnTag2)  # pyright: ignore[reportPrivateUsage]

    ### Assert
    assert expectedDateTimeStr2 == date2

    ### Third Test, no offset in date tag, but has offset tag!
    expectedDateTimeStr3 = "2025-01-01T10:48:44+02:00"

    ### Execute
    date3 = MediaFile._findCreationTime(noOffsetInTagButHasOffsetTag)  # pyright: ignore[reportPrivateUsage]

    ### Assert
    assert expectedDateTimeStr3 == date3


noOffsetInTagOffsetTagWrong: dict[str, str] = {
    "SourceFile": "myFileName.jpg",  # we need a file name to display the error message
    "ExifIFD:CreateDate": "2025-01-01T10:48:44",
    "ExifIFD:OffsetTimeDigitized": "+02:000",  # <- correct offset for CreateDate
}


def test_findCreationTime_hasOffsetTagButOffsetWrong():
    # Check that ValueError is raised
    with raises(ValueError):
        MediaFile._findCreationTime(noOffsetInTagOffsetTagWrong)  # pyright: ignore[reportPrivateUsage]


noOffset: dict[str, str] = {
    "ExifIFD:DateTimeOriginal": "2025-01-01T10:48:44",
}


def test_findCreationTime_noOffset_ConsiderUTC():
    ### Prepare the test
    expectedDateTimeStr = "2025-01-01T10:48:44+00:00"

    ### Execute
    date = MediaFile._findCreationTime(noOffset)  # pyright: ignore[reportPrivateUsage]

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
    date = MediaFile._findCreationTime(noDates)  # pyright: ignore[reportPrivateUsage]

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
    date = MediaFile._findCreationTime(GPSCoordinatesDict)  # pyright: ignore[reportPrivateUsage]

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
    date = MediaFile._findCreationTime(GPSCoordinatesSouthWestDict)  # pyright: ignore[reportPrivateUsage]

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
    date = MediaFile._findCreationTime(GPSCoordinatesIgnoreOffsetDict)  # pyright: ignore[reportPrivateUsage]

    ### Assert
    assert expectedDateTimeStr == date


"""
inferDateFromNeighbours

- Get the date from the previous item

"""

# This list contains an item without date on position 1, and elements with dates in positions 0 and 2 (just right next
# to the dateless item)
exifTagsForTest1 = [
    {
        "SourceFile": "C:/Users/mundo/OneDrive/Desktop/EXIFPhotoRenamer/FotosTest/A/028.png",
        "XMP-photoshop:DateCreated": "2018-12-12T18:40:16+00:00",
    },
    {"SourceFile": "C:/Users/mundo/OneDrive/Desktop/EXIFPhotoRenamer/FotosTest/A/042.mov"},
    {
        "SourceFile": "C:/Users/mundo/OneDrive/Desktop/EXIFPhotoRenamer/FotosTest/A/141.png",
        "XMP-photoshop:DateCreated": "2018-12-09T18:45:56+00:00",
    },
    {
        "SourceFile": "C:/Users/mundo/OneDrive/Desktop/EXIFPhotoRenamer/FotosTest/A/198.mp4",
        "QuickTime:CreateDate": "2018-06-12T19:10:27+01:00",
    },
    {
        "SourceFile": "C:/Users/mundo/OneDrive/Desktop/EXIFPhotoRenamer/FotosTest/A/2024-06-05 - Insta_FaceBook 1.jpg",
        "ExifIFD:CreateDate": "2024-06-05T18:16:47+01:00",
    },
    {
        "SourceFile": "C:/Users/mundo/OneDrive/Desktop/EXIFPhotoRenamer/FotosTest/A/2025-01-01 - iPhone 13 mini 1.HEIC",
        "ExifIFD:DateTimeOriginal": "2025-01-01T10:48:44+00:00",
    },
]


# Test one is the simplest case, where the dateless item has dated items on both sides, just next to it
def test_inferDateFromNeighboursTest1():
    ### Prepare
    mediaFileList = [MediaFile.fromExifTags(tags) for tags in exifTagsForTest1]
    expectedDateFromLeft = "2018-12-12T18:41:16+00:00"
    expectedDateFromRight = "2018-12-09T18:44:56+00:00"
    datelessIdx = 1

    ### Execute
    dateLeft, dateRight = inferDateFromNeighbours(datelessIdx, mediaFileList)

    ### Assert
    assert expectedDateFromLeft == dateLeft
    assert expectedDateFromRight == dateRight


# This list contains an item without date on position 2, and elements with dates in positions 0 and 4 (so, there are
# more dateless items surrounding the date we want to infer)
exifTagsForTest2 = [
    {
        "SourceFile": "C:/Users/mundo/OneDrive/Desktop/EXIFPhotoRenamer/FotosTest/A/028.png",
        "XMP-photoshop:DateCreated": "2018-12-12T18:40:16+00:00",
    },
    {"SourceFile": "C:/Users/mundo/OneDrive/Desktop/EXIFPhotoRenamer/FotosTest/A/042.mov"},
    {"SourceFile": "C:/Users/mundo/OneDrive/Desktop/EXIFPhotoRenamer/FotosTest/A/141.png"},
    {"SourceFile": "C:/Users/mundo/OneDrive/Desktop/EXIFPhotoRenamer/FotosTest/A/198.mp4"},
    {"SourceFile": "C:/Users/mundo/OneDrive/Desktop/EXIFPhotoRenamer/FotosTest/A/2024-06-05 - Insta_FaceBook 1.jpg"},
    {
        "SourceFile": "C:/Users/mundo/OneDrive/Desktop/EXIFPhotoRenamer/FotosTest/A/2025-01-01 - iPhone 13 mini 1.HEIC",
        "ExifIFD:DateTimeOriginal": "2025-01-01T10:48:44+00:00",
    },
]


# Test two has a dateless item with dated items on both sides of the list, but with more dateless items in between
def test_inferDateFromNeighboursTest2():
    ### Prepare
    mediaFileList = [MediaFile.fromExifTags(tags) for tags in exifTagsForTest2]
    expectedDateFromLeft = "2018-12-12T18:42:16+00:00"
    expectedDateFromRight = "2025-01-01T10:45:44+00:00"
    datelessIdx = 2

    ### Execute
    dateLeft, dateRight = inferDateFromNeighbours(datelessIdx, mediaFileList)

    ### Assert
    assert expectedDateFromLeft == dateLeft
    assert expectedDateFromRight == dateRight


# This list contains no dated item on it, so any check on its members will return None on both sides
exifTagsForTest3 = [
    {"SourceFile": "C:/Users/mundo/OneDrive/Desktop/EXIFPhotoRenamer/FotosTest/A/028.png"},
    {"SourceFile": "C:/Users/mundo/OneDrive/Desktop/EXIFPhotoRenamer/FotosTest/A/042.mov"},
    {"SourceFile": "C:/Users/mundo/OneDrive/Desktop/EXIFPhotoRenamer/FotosTest/A/141.png"},
    {"SourceFile": "C:/Users/mundo/OneDrive/Desktop/EXIFPhotoRenamer/FotosTest/A/198.mp4"},
    {"SourceFile": "C:/Users/mundo/OneDrive/Desktop/EXIFPhotoRenamer/FotosTest/A/2024-06-05 - Insta_FaceBook 1.jpg"},
    {"SourceFile": "C:/Users/mundo/OneDrive/Desktop/EXIFPhotoRenamer/FotosTest/A/2025-01-01 - iPhone 13 mini 1.HEIC"},
]


# Test two has a dateless item with dated items on both sides of the list, but with more dateless items in between
def test_inferDateFromNeighboursTest3():
    ### Prepare
    mediaFileList = [MediaFile.fromExifTags(tags) for tags in exifTagsForTest3]
    expectedDateFromLeft = None
    expectedDateFromRight = None

    ### Execute
    for idx in range(len(exifTagsForTest3)):
        dateLeft, dateRight = inferDateFromNeighbours(idx, mediaFileList)

        ### Assert
        assert expectedDateFromLeft == dateLeft
        assert expectedDateFromRight == dateRight


# This list contains no dated item on the left side, to check we don't overflow
exifTagsForTest4Left = [
    {"SourceFile": "C:/Users/mundo/OneDrive/Desktop/EXIFPhotoRenamer/FotosTest/A/028.png"},
    {"SourceFile": "C:/Users/mundo/OneDrive/Desktop/EXIFPhotoRenamer/FotosTest/A/042.mov"},
    {"SourceFile": "C:/Users/mundo/OneDrive/Desktop/EXIFPhotoRenamer/FotosTest/A/141.png"},
    {"SourceFile": "C:/Users/mundo/OneDrive/Desktop/EXIFPhotoRenamer/FotosTest/A/198.mp4"},
    {"SourceFile": "C:/Users/mundo/OneDrive/Desktop/EXIFPhotoRenamer/FotosTest/A/2024-06-05 - Insta_FaceBook 1.jpg"},
    {
        "SourceFile": "C:/Users/mundo/OneDrive/Desktop/EXIFPhotoRenamer/FotosTest/A/2025-01-01 - iPhone 13 mini 1.HEIC",
        "ExifIFD:DateTimeOriginal": "2025-01-01T10:48:44+00:00",
    },
]

exifTagsForTest4Right = [
    {
        "SourceFile": "C:/Users/mundo/OneDrive/Desktop/EXIFPhotoRenamer/FotosTest/A/028.png",
        "ExifIFD:DateTimeOriginal": "2025-01-01T10:48:44+00:00",
    },
    {"SourceFile": "C:/Users/mundo/OneDrive/Desktop/EXIFPhotoRenamer/FotosTest/A/042.mov"},
    {"SourceFile": "C:/Users/mundo/OneDrive/Desktop/EXIFPhotoRenamer/FotosTest/A/141.png"},
    {"SourceFile": "C:/Users/mundo/OneDrive/Desktop/EXIFPhotoRenamer/FotosTest/A/198.mp4"},
    {"SourceFile": "C:/Users/mundo/OneDrive/Desktop/EXIFPhotoRenamer/FotosTest/A/2024-06-05 - Insta_FaceBook 1.jpg"},
    {"SourceFile": "C:/Users/mundo/OneDrive/Desktop/EXIFPhotoRenamer/FotosTest/A/2025-01-01 - iPhone 13 mini 1.HEIC"},
]


# These lists have only dates on one side, to make sure we don't overflow the search or somehting silly
def test_inferDateFromNeighboursTest4():
    ### Prepare
    mediaFileList = [MediaFile.fromExifTags(tags) for tags in exifTagsForTest4Left]
    expectedDateFromLeft = None
    expectedDateFromRight = "2025-01-01T10:45:44+00:00"
    datelessIdx = 2

    ### Execute
    dateLeft, dateRight = inferDateFromNeighbours(datelessIdx, mediaFileList)

    ### Assert
    assert expectedDateFromLeft == dateLeft
    assert expectedDateFromRight == dateRight

    ### Prepare
    mediaFileList = [MediaFile.fromExifTags(tags) for tags in exifTagsForTest4Right]
    expectedDateFromLeft = "2025-01-01T10:50:44+00:00"
    expectedDateFromRight = None
    datelessIdx = 2

    ### Execute
    dateLeft, dateRight = inferDateFromNeighbours(datelessIdx, mediaFileList)

    ### Assert
    assert expectedDateFromLeft == dateLeft
    assert expectedDateFromRight == dateRight
