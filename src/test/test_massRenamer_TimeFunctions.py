from pytest import fixture, raises
from massRenamer.massRenamerClasses import *
from exiftool import ExifToolHelper, ExifTool

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
    assert getTimeOffset({"EXIF:CreateDate": "1234:12:23 01:02:03", "EXIF:OffsetTimeDigitized": "+02:00"}, "EXIF:CreateDate") == "1234:12:23 01:02:03+02:00"
    assert getTimeOffset({"EXIF:CreateDate": "1111:12:21 02:04:05", "EXIF:OffsetTimeDigitized": "-05:00"}, "EXIF:CreateDate") == "1111:12:21 02:04:05-05:00"
    assert getTimeOffset({"EXIF:CreateDate": "1111:12:21 02:04:05", "EXIF:OffsetTimeDigitized": "Z"}, "EXIF:CreateDate") == "1111:12:21 02:04:05+00:00"

def test_getTimeOffset_DateTimeOriginalWithOffsetTimeOriginal():
    assert getTimeOffset({"EXIF:DateTimeOriginal": "1234:12:23 01:02:03", "EXIF:OffsetTimeOriginal": "+02:00"}, "EXIF:DateTimeOriginal") == "1234:12:23 01:02:03+02:00"
    assert getTimeOffset({"EXIF:DateTimeOriginal": "1111:12:21 02:04:05", "EXIF:OffsetTimeOriginal": "-05:00"}, "EXIF:DateTimeOriginal") == "1111:12:21 02:04:05-05:00"
    assert getTimeOffset({"EXIF:DateTimeOriginal": "1111:12:21 02:04:05", "EXIF:OffsetTimeOriginal": "Z"}, "EXIF:DateTimeOriginal") == "1111:12:21 02:04:05+00:00"

def test_getTimeOffset_DateTimeTagWithoutOffsetInfo():
    assert getTimeOffset({"EXIF:CreateDate": "1111:12:21 02:04:05"}, "EXIF:CreateDate") == "1111:12:21 02:04:05+00:00"
    assert getTimeOffset({"EXIF:DateTimeOriginal": "1234:12:23 01:02:03"}, "EXIF:DateTimeOriginal") == "1234:12:23 01:02:03+00:00"

def test_getTimeOffset_OtherDateTags():
    assert getTimeOffset({"XMP:CreateDate": "1111:12:21 02:04:05"}, "XMP:CreateDate") == "1111:12:21 02:04:05+00:00"
    assert getTimeOffset({"QuickTime:DateTimeOriginal": "1234:12:23 01:02:03"}, "QuickTime:DateTimeOriginal") == "1234:12:23 01:02:03+00:00"

def test_getTimeOffset_NoDateTags():
    with raises(Exception) as e_info:
        getTimeOffset({"EXIF:Make": "Apple"}, "EXIF:Make")
    with raises(Exception) as e_info:
        getTimeOffset({"QuickTime:DateTimeOriginal": "11:33:55 01:02:03"}, "QuickTime:DateTimeOriginal") == "1234:12:23 01:02:03+00:00"

"""
getTZAwareness()

- Date is TZ Aware
- Date is TZ Aware with Z
- Date is TZ Naive
- Date is not a Date
"""

def test_getTZAwareness_testAware():
    date:str = "1234:12:12 12:12:12+05:00"
    assert getTZAwareness(date) == TZ_AWARENESS.AWARE

def test_getTZAwareness_testAwareWithZ():
    date:str = "1234:12:12 12:12:12Z"
    assert getTZAwareness(date) == TZ_AWARENESS.Z_AWARE

def test_getTZAwareness_testNaive():
    date:str = "1234:12:12 12:12:12"
    assert getTZAwareness(date) == TZ_AWARENESS.NAIVE

def test_getTZAwareness_testNotADate():
    date:str = "1234:12:12 12:"
    assert getTZAwareness(date) == None

"""
findCreationTime()

- Has a date tag and returns it in UTC format (no +/-XX)
- Has many date tags, returns the oldest in UTC format
- Has no date tags, returns None
"""

def test_findCreationTime_hasOneTag():
    assert findCreationTime({"EXIF:DateTimeOriginal": "2013:12:03 12:01:02"}) ==  "2013:12:03 12:01:02+00:00"
    assert findCreationTime({"QuickTime:CreateDate": "2013:12:03 12:01:02"}) ==  "2013:12:03 12:01:02+00:00"
    assert findCreationTime({"QuickTime:CreateDate": "2013:12:03 12:01:02+05:00"}) ==  "2013:12:03 12:01:02+05:00"

def test_findCreationTime_hasManyTags():
    assert findCreationTime({"EXIF:DateTimeOriginal": "2013:12:03 12:01:02", "EXIF:CreateDate": "2014:12:12 12:45:32"}) ==  "2013:12:03 12:01:02+00:00"
    assert findCreationTime({"EXIF:DateTimeOriginal": "2013:12:03 12:01:02", "EXIF:CreateDate": "2013:12:03 13:01:00+01:00"}) ==  "2013:12:03 13:01:00+01:00"

def test_findCreationTime_preferDatesWithOffset():
    assert findCreationTime({"EXIF:DateTimeOriginal": "2013:12:03 12:01:02", "XMP:DateTimeOriginal": "2014:05:10 15:20:02", "EXIF:CreateDate": "2013:12:03 13:01:02+01:00"}) ==  "2013:12:03 13:01:02+01:00"

def test_findCreationTime_doesntHaveTimeTag():
    assert findCreationTime({"EXIF:Make": "Apple"}) ==  None

"""
inferDateFromNeighbours

- Get the date from the previous item

"""

@fixture
def listPhotoOneDatelessTest1():
    exifData0 = {"SourceFile": "fakeFile1.jpg", "EXIF:Make": "Apple", "EXIF:Model": "iPhone 8", "EXIF:CreateDate": "1234:12:12 11:22:33"}
    exifData1 = {"SourceFile": "fakeFile2.jpg", "EXIF:Make": "Apple", "EXIF:Model": "iPhone 8"}
    exifData2 = {"SourceFile": "fakeFile3.jpg", "EXIF:Make": "Apple", "EXIF:Model": "iPhone 8", "EXIF:CreateDate": "1234:12:12 11:30:33"}
    return [MediaFile.fromExifTags(exifData0), MediaFile.fromExifTags(exifData1), MediaFile.fromExifTags(exifData2)]

def test_inferDateFromNeighboursTest1(listPhotoOneDatelessTest1):
    listOfItems:List[MediaFile] = listPhotoOneDatelessTest1
    assert inferDateFromNeighbours(1, listOfItems) == "1234:12:12 11:29:33+00:00"

@fixture
def listPhotoOneDatelessTest2():
    exifData0 = {"SourceFile": "fakeFile1.jpg", "EXIF:Make": "Apple", "EXIF:Model": "iPhone 8"}
    exifData1 = {"SourceFile": "fakeFile2.jpg", "EXIF:Make": "Apple", "EXIF:Model": "iPhone 8"}
    exifData2 = {"SourceFile": "fakeFile3.jpg", "EXIF:Make": "Apple", "EXIF:Model": "iPhone 8", "EXIF:CreateDate": "1234:12:12 11:30:33"}
    return [MediaFile.fromExifTags(exifData0), MediaFile.fromExifTags(exifData1), MediaFile.fromExifTags(exifData2)]

def test_inferDateFromNeighboursTest2(listPhotoOneDatelessTest2):
    listOfItems:List[MediaFile] = listPhotoOneDatelessTest2
    assert inferDateFromNeighbours(1, listOfItems) == "1234:12:12 11:29:33+00:00"

@fixture
def listPhotoOneDatelessPreviousTest3():
    photoList = [ {"SourceFile": "fakeFile1.jpg", "EXIF:Make": "Apple", "EXIF:Model": "iPhone 8", "EXIF:CreateDate": "1234:12:12 11:22:33"},
        {"SourceFile": "fakeFile3.jpg", "EXIF:Make": "Apple", "EXIF:Model": "iPhone 8", "EXIF:CreateDate": "1234:12:12 11:30:33"},
        {"SourceFile": "fakeFile1.jpg", "EXIF:Make": "Apple", "EXIF:Model": "iPhone 8"},
        {"SourceFile": "fakeFile2.jpg", "EXIF:Make": "Apple", "EXIF:Model": "iPhone 8"},
        {"SourceFile": "fakeFile3.jpg", "EXIF:Make": "Apple", "EXIF:Model": "iPhone 8", "EXIF:CreateDate": "1234:12:12 11:40:33"}]
    return [MediaFile.fromExifTags(photo) for photo in photoList]

def test_inferDateFromNeighboursTest3(listPhotoOneDatelessPreviousTest3):
    listOfItems:List[MediaFile] = listPhotoOneDatelessPreviousTest3
    assert inferDateFromNeighbours(3, listOfItems) == "1234:12:12 11:32:33+00:00"

@fixture
def listPhotoOneDatelessPreviousTest4():
    photoList = [ {"SourceFile": "fakeFile1.jpg", "EXIF:Make": "Apple", "EXIF:Model": "iPhone 8"},
        {"SourceFile": "fakeFile3.jpg", "EXIF:Make": "Apple", "EXIF:Model": "iPhone 8"},
        {"SourceFile": "fakeFile1.jpg", "EXIF:Make": "Apple", "EXIF:Model": "iPhone 8"},
        {"SourceFile": "fakeFile2.jpg", "EXIF:Make": "Apple", "EXIF:Model": "iPhone 8"},
        {"SourceFile": "fakeFile3.jpg", "EXIF:Make": "Apple", "EXIF:Model": "iPhone 8", "EXIF:CreateDate": "1234:12:12 11:40:33"}]
    return [MediaFile.fromExifTags(photo) for photo in photoList]

def test_inferDateFromNeighboursTest4(listPhotoOneDatelessPreviousTest4):
    listOfItems:List[MediaFile] = listPhotoOneDatelessPreviousTest4
    assert inferDateFromNeighbours(2, listOfItems) == "1234:12:12 11:38:33+00:00"

@fixture
def listPhotoOneDatelessPreviousTest5():
    photoList = [ {"SourceFile": "fakeFile1.jpg", "EXIF:Make": "Apple", "EXIF:Model": "iPhone 8"},
        {"SourceFile": "fakeFile3.jpg", "EXIF:Make": "Apple", "EXIF:Model": "iPhone 8"},
        {"SourceFile": "fakeFile1.jpg", "EXIF:Make": "Apple", "EXIF:Model": "iPhone 8"},
        {"SourceFile": "fakeFile2.jpg", "EXIF:Make": "Apple", "EXIF:Model": "iPhone 8"},
        {"SourceFile": "fakeFile3.jpg", "EXIF:Make": "Apple", "EXIF:Model": "iPhone 8"}]
    return [MediaFile.fromExifTags(photo) for photo in photoList]

def test_inferDateFromNeighboursTest5(listPhotoOneDatelessPreviousTest5):
    listOfItems:List[MediaFile] = listPhotoOneDatelessPreviousTest5
    assert inferDateFromNeighbours(2, listOfItems) == None


def test_fixDateInteractive_Success(listPhotoOneDatelessPreviousTest3, mocker):
    listOfItems:List[MediaFile] = listPhotoOneDatelessPreviousTest3
    datelessItem = 2
    fileName = listOfItems[datelessItem].getFileName()
    resonse: str = "[File]          FileInodeChangeDate             : 2024:03:13 14:22:20+00:00\n"\
                    "[QuickTime]     CreateDate                      : 2018:02:28 02:25:37\n"\
                    "[QuickTime]     ModifyDate                      : 2018:02:28 02:25:39\n"\
                    "[QuickTime]     TrackCreateDate                 : 2018:02:28 02:25:37\n"\
                    "[QuickTime]     TrackModifyDate                 : 2018:02:28 02:25:39\n"\
                    "[QuickTime]     MediaCreateDate                 : 2018:02:28 02:25:37\n"\
                    "[QuickTime]     MediaModifyDate                 : 2018:02:28 02:25:39"
    mocker.patch("exiftool.ExifTool.execute", return_value=resonse)
    mocker.patch("massRenamer.massRenamerClasses._getInput", return_value='2')

    assert fixDateInteractive(datelessItem, listOfItems) == "2018:02:28 02:25:37"
    ExifTool.execute.assert_called_with("-time:all", "-G1", "-a", "-s", str(fileName))

def test_fixDateInteractive_CantParseTime(listPhotoOneDatelessPreviousTest3, mocker):
    listOfItems:List[MediaFile] = listPhotoOneDatelessPreviousTest3
    datelessItem = 2
    fileName = listOfItems[datelessItem].getFileName()
    resonse: str = "[File]          FileInodeChangeDate             : 2024:03:13 14:22:20+00:00\n"\
                    "[QuickTime]     CreateDate                      : AAAA:BB:CC 02:25:37\n"\
                    "[QuickTime]     ModifyDate                      : 2018:02:28 02:25:39\n"\
                    "[QuickTime]     TrackCreateDate                 : 2018:02:28 02:25:37\n"\
                    "[QuickTime]     TrackModifyDate                 : 2018:02:28 02:25:39\n"\
                    "[QuickTime]     MediaCreateDate                 : 2018:02:28 02:25:37\n"\
                    "[QuickTime]     MediaModifyDate                 : 2018:02:28 02:25:39"
    mocker.patch("exiftool.ExifTool.execute", return_value=resonse)
    mocker.patch("massRenamer.massRenamerClasses._getInput", return_value='2')

    assert fixDateInteractive(datelessItem, listOfItems) == None
    ExifTool.execute.assert_called_with("-time:all", "-G1", "-a", "-s", str(fileName))

def test_fixDateInteractive_SaveProgressToDisk(listPhotoOneDatelessPreviousTest3, mocker):
    listOfItems:List[MediaFile] = listPhotoOneDatelessPreviousTest3
    datelessItem = 2
    fileName = listOfItems[datelessItem].getFileName()
    resonse: str = "[File]          FileInodeChangeDate             : 2024:03:13 14:22:20+00:00\n"\
                    "[QuickTime]     CreateDate                      : AAAA:BB:CC 02:25:37\n"\
                    "[QuickTime]     ModifyDate                      : 2018:02:28 02:25:39\n"\
                    "[QuickTime]     TrackCreateDate                 : 2018:02:28 02:25:37\n"\
                    "[QuickTime]     TrackModifyDate                 : 2018:02:28 02:25:39\n"\
                    "[QuickTime]     MediaCreateDate                 : 2018:02:28 02:25:37\n"\
                    "[QuickTime]     MediaModifyDate                 : 2018:02:28 02:25:39"

    # Mock a file being opened, return the "open" object on m
    m = mocker.patch('massRenamer.massRenamerClasses.open', mocker.mock_open())
    mocker.patch("exiftool.ExifTool.execute", return_value=resonse)
    mocker.patch("massRenamer.massRenamerClasses._getInput", return_value='-1')
    # mocker.patch("massRenamer.massRenamerClasses.storeMediaFileList")
    with raises(SystemExit) as pytest_wrapped_e:
        fixDateInteractive(datelessItem, listOfItems)
    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code == 0
    # check that open was called with a Path and the 'w' mode
    m.assert_called_once_with(Path("MediaFileList.txt"), "w")
    # And now, check it was written: notice that now we don't use m.write, but m().write!
    m().write.assert_called_once_with(str(listOfItems))
    ExifTool.execute.assert_called_with("-time:all", "-G1", "-a", "-s", str(fileName))

def test_fixDateInteractive_SkipFile(listPhotoOneDatelessPreviousTest3, mocker):
    listOfItems:List[MediaFile] = listPhotoOneDatelessPreviousTest3
    datelessItem = 2
    fileName = listOfItems[datelessItem].getFileName()
    resonse: str = "[File]          FileInodeChangeDate             : 2024:03:13 14:22:20+00:00\n"\
                    "[QuickTime]     CreateDate                      : AAAA:BB:CC 02:25:37\n"\
                    "[QuickTime]     ModifyDate                      : 2018:02:28 02:25:39\n"\
                    "[QuickTime]     TrackCreateDate                 : 2018:02:28 02:25:37\n"\
                    "[QuickTime]     TrackModifyDate                 : 2018:02:28 02:25:39\n"\
                    "[QuickTime]     MediaCreateDate                 : 2018:02:28 02:25:37\n"\
                    "[QuickTime]     MediaModifyDate                 : 2018:02:28 02:25:39"
    mocker.patch("exiftool.ExifTool.execute", return_value=resonse)
    mocker.patch("massRenamer.massRenamerClasses._getInput", return_value='0')

    assert fixDateInteractive(datelessItem, listOfItems) == None
    ExifTool.execute.assert_called_with("-time:all", "-G1", "-a", "-s", str(fileName))

def test_fixDateInteractive_WeirdInput(listPhotoOneDatelessPreviousTest3, mocker):
    listOfItems:List[MediaFile] = listPhotoOneDatelessPreviousTest3
    datelessItem = 2
    fileName = listOfItems[datelessItem].getFileName()
    resonse: str = "[File]          FileInodeChangeDate             : 2024:03:13 14:22:20+00:00\n"\
                    "[QuickTime]     CreateDate                      : AAAA:BB:CC 02:25:37\n"\
                    "[QuickTime]     ModifyDate                      : 2018:02:28 02:25:39\n"\
                    "[QuickTime]     TrackCreateDate                 : 2018:02:28 02:25:37\n"\
                    "[QuickTime]     TrackModifyDate                 : 2018:02:28 02:25:39\n"\
                    "[QuickTime]     MediaCreateDate                 : 2018:02:28 02:25:37\n"\
                    "[QuickTime]     MediaModifyDate                 : 2018:02:28 02:25:39"
    mocker.patch("exiftool.ExifTool.execute", return_value=resonse)
    mocker.patch("massRenamer.massRenamerClasses._getInput", return_value='A')

    assert fixDateInteractive(datelessItem, listOfItems) == None
    ExifTool.execute.assert_called_with("-time:all", "-G1", "-a", "-s", str(fileName))