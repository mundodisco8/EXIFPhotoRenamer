from src.massRenamer.massRenamerClasses import *

"""
MediaFile.fromExifTags Class test:
- Creation
- repr method prints the data in the correct format (so we can init more instances of the MediaFile class out of it)
"""


def test_MediaFile_Creation():
    exifData = {
        "SourceFile": "fakeFile.jpg",
        "EXIF:Make": "Apple",
        "EXIF:Model": "iPhone 8",
        "EXIF:CreateDate": "1234:12:12 11:22:33",
    }
    testInstance = MediaFile.fromExifTags(exifData)
    assert isinstance(testInstance, MediaFile)
    assert testInstance._fileName == Path("fakeFile.jpg")
    assert testInstance._dateTime == "1234:12:12 11:22:33+00:00"
    assert testInstance._sidecar == None
    assert testInstance._source == "iPhone 8"


def test_MediaFile_repr():
    exifData = {
        "SourceFile": "fakeFile.jpg",
        "EXIF:Make": "Apple",
        "EXIF:Model": "iPhone 8",
        "EXIF:CreateDate": "1234:12:12 11:22:33",
    }
    sourceInstance = MediaFile.fromExifTags(exifData)
    testInstance = eval(sourceInstance.__repr__())
    assert isinstance(testInstance, type(sourceInstance))
    assert testInstance._fileName == sourceInstance._fileName
    assert testInstance._dateTime == sourceInstance._dateTime
    assert testInstance._sidecar == sourceInstance._sidecar
    assert testInstance._source == sourceInstance._source


def test_mediaFile_setTime_Success():
    mediaFile = MediaFile(Path("fakeFile.jpg"), None, "WhatsApp")
    newTime = "1234:12:12 11:22:33"
    mediaFile.setTime(newTime)
    assert mediaFile.getTime() == "1234:12:12 11:22:33+00:00"
    newTime = "1234:12:12 10:20:30+03:00"
    mediaFile.setTime(newTime)
    assert mediaFile.getTime() == "1234:12:12 10:20:30+03:00"
    newTime = "1234:12:12 00:00:00Z"
    mediaFile.setTime(newTime)
    assert mediaFile.getTime() == "1234:12:12 00:00:00+00:00"


def test_mediaFile_setTime_BadTime():
    mediaFile = MediaFile(Path("fakeFile.jpg"), None, "WhatsApp")
    newTime = "1234:12:12 11:22"

    mediaFile.setTime(newTime)
    assert mediaFile.getTime() == None
