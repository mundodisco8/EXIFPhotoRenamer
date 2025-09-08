from pathlib import Path
from src.massRenamer.massRenamerClasses import MediaFile

"""
MediaFile.fromExifTags Class test:
- Creation
- repr method prints the data in the correct format (so we can init more instances of the MediaFile class out of it)
"""


def test_MediaFile_Creation():
    exifData = {
        "SourceFile": "fakeFile.jpg",
        "ExifIFD:Make": "Apple",
        "ExifIFD:Model": "iPhone 8",
        "ExifIFD:CreateDate": "1234-12-12 11:22:33",
    }
    testInstance = MediaFile.fromExifTags(exifData)
    assert isinstance(testInstance, MediaFile)
    assert testInstance.fileName == Path("fakeFile.jpg")
    assert testInstance.dateTime == "1234-12-12T11:22:33+00:00"
    assert testInstance.sidecar is None
    assert testInstance.source == "iPhone 8"
    assert testInstance.EXIFTags == exifData


def test_MediaFile_repr():
    exifData = {
        "SourceFile": "fakeFile.jpg",
        "ExifIFD:Make": "Apple",
        "ExifIFD:Model": "iPhone 8",
        "ExifIFD:CreateDate": "1234-12-12T11:22:33",
    }
    sourceInstance = MediaFile.fromExifTags(exifData)
    testInstance = eval(sourceInstance.__repr__())
    # assert isinstance(testInstance, type(sourceInstance))
    # assert testInstance.fileName == sourceInstance.fileName
    # assert testInstance.dateTime == sourceInstance.dateTime
    # assert testInstance.sidecar == sourceInstance.sidecar
    # assert testInstance.source == sourceInstance.source
    assert testInstance.EXIFTags == exifData
