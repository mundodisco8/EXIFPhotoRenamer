import pytest
from massRenamer.massRenamerClasses import *
from pytest import raises

"""tc
PhotoFile Class test:
- Creation
"""

def test_PhotoFile_Creation():
    exifData = {"sourceFile": "fakeFile.jpg", "EXIF:Make": "Apple", "EXIF:Model": "iPhone 8", "EXIF:CreateDate": "1234:12:12 11:22:33"}
    testInstance = PhotoFile(exifData)
    assert isinstance(testInstance, PhotoFile)

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
isScreenshot()
- Has "*:UserComment" tag with value "Screenshot", returns true
- Doesn't have a "*:UserComment" tag, returns false
"""

def test_isScreenshot_AndItIs():
    assert isScreenShot({"XMP:UserComment": "Screenshot"}) == True
    assert isScreenShot({"EXIF:UserComment": "Screenshot"}) == True
    assert isScreenShot({"Silly:UserComment": "ScrEEnShot"}) == True

def test_isScreenshot_AndItIsNot():
    assert isScreenShot({"XMP:OneTag": "Screenshot"}) == False
    assert isScreenShot({"XMP:UserComment": "Screen"}) == False

"""
isInstaOrFace()
- Has "*:UserComment" tag with the correct values, returns true
- Doesn't have a "*:UserComment" tag, or it has but without the expected values, returns false
"""

def test_isInstaOrFace_AndItIs():
    assert isInstaOrFace({"XMP:Software": "faCeBook"}) == True
    assert isInstaOrFace({"EXIF:Software": "Some Facebook App"}) == True
    assert isInstaOrFace({"Silly:Software": "InstaInstagramgram"}) == True

def test_isInstaOrFace_AndItIsNot():
    assert isInstaOrFace({"XMP:OneTag": "facebook"}) == False
    assert isInstaOrFace({"XMP:Software": "Adobe"}) == False


"""
isPicsArt()
- It's from picsart, returns true
- It's not, returns false
"""

def test_isPicsArt_AndItIs():
    assert isPicsArt({"EXIF:Software": "PicsArt"}) == True

def test_isPicsArt_AndItIsNot():
    # wrong tag and correct content
    assert isPicsArt({"XMP:Software": "PicsArt"}) == False
    # wrong tag and wrong capitalisation
    assert isPicsArt({"XMP:Software": "picsart"}) == False
    # wrong tag and wrong content
    assert isPicsArt({"XMP:OneTag": "facebook"}) == False
    # wrong tag, content contains the string, but still wrong content
    assert isPicsArt({"XMP:Software": "PicsArt and something else"}) == False

"""
getFileSource()
- Test file has one Model tag
- Test file has two model tags, but they have the same value
- Test file has two or more model tags, and they have more than one value

- Test file has one make tag
- Test file has two make tags, but they have the same value
- Test file has two or more make tags, and they have more than one value

- An Screenshot
- An Instagram Photo
- A PicsArt Photo
- Something else (WhatsApp)
"""

def test_getFileSource_ModelOneTag():
    """
    Success when the EXIF data has only one "Model" tag
    """
    assert getFileSource({"EXIF:Model": "Device X"}) == "Device X"

def test_getFileSource_ModelManyTagsSameValue():
    """
    Success when the EXIF data has two or more "Model" tags, with same value
    """
    assert getFileSource({"EXIF:Model": "Device X", "XMP:Model": "Device X"}) == "Device X"
    assert getFileSource({"EXIF:Model": "Device X", "XMP:Model": "Device X", "Something:Model": "Device X", "Silly:Model": "Device X"}) == "Device X"

def test_getFileSource_ModelManyTagsDiffValue():
    """
    Raise exception if more than one Makes
    """
    with raises(Exception) as e_info:
        getFileSource({"EXIF:Model": "Device X", "XMP:Model": "Device Y"})

def test_getFileSource_MakeOneTag():
    """
    Success when the EXIF data has only one "MAke" tag
    """
    assert getFileSource({"EXIF:Make": "Brand X"}) == "Brand X"

def test_getFileSource_MakeManyTagsSameValue():
    """
    Success when the EXIF data has two or more "Make" tags, with same value
    """
    assert getFileSource({"EXIF:Make": "Brand X", "XMP:Make": "Brand X"}) == "Brand X"
    assert getFileSource({"EXIF:Make": "Brand X", "XMP:Make": "Brand X", "Something:Make": "Brand X", "Silly:Make": "Brand X"}) == "Brand X"

def test_getFileSource_MakeManyTagsDiffValue():
    with raises(Exception) as e_info:
        getFileSource({"EXIF:Make": "Brand X", "XMP:Make": "Brand Y"})

def test_getFileSource_Screenshot():
    """
    Success when the file is a screenshot
    """
    assert getFileSource({"EXIF:UserComment": "Screenshot"}) == "Screenshot"

def test_getFileSource_Instagram():
    """
    Success when the file is from instagram
    """
    assert getFileSource({"EXIF:Software": "Something Instagram"}) == "Insta_FaceBook"

def test_getFileSource_PicsArt():
    """
    Success when the file is from Picsart
    """
    assert getFileSource({"EXIF:Software": "PicsArt"}) == "PicsArt"

def test_getFileSource_WhatsApp():
    """
    Success when the file is tagged as from "WhatsApp"
    """
    assert getFileSource({"EXIF:SomeTag": "SomeValue"}) == "WhatsApp"

"""
inferDateFromNeighbours

- Get the date from the previous item

"""

@pytest.fixture
def listPhotoOneDatelessTest1():
    exifData0 = {"sourceFile": "fakeFile1.jpg", "EXIF:Make": "Apple", "EXIF:Model": "iPhone 8", "EXIF:CreateDate": "1234:12:12 11:22:33"}
    exifData1 = {"sourceFile": "fakeFile2.jpg", "EXIF:Make": "Apple", "EXIF:Model": "iPhone 8"}
    exifData2 = {"sourceFile": "fakeFile3.jpg", "EXIF:Make": "Apple", "EXIF:Model": "iPhone 8", "EXIF:CreateDate": "1234:12:12 11:30:33"}
    return [PhotoFile(exifData0), PhotoFile(exifData1), PhotoFile(exifData2)]

def test_inferDateFromNeighboursTest1(listPhotoOneDatelessTest1):
    listOfItems:List[PhotoFile] = listPhotoOneDatelessTest1

@pytest.fixture
def listPhotoOneDatelessTest2():
    exifData0 = {"sourceFile": "fakeFile1.jpg", "EXIF:Make": "Apple", "EXIF:Model": "iPhone 8"}
    exifData1 = {"sourceFile": "fakeFile2.jpg", "EXIF:Make": "Apple", "EXIF:Model": "iPhone 8"}
    exifData2 = {"sourceFile": "fakeFile3.jpg", "EXIF:Make": "Apple", "EXIF:Model": "iPhone 8", "EXIF:CreateDate": "1234:12:12 11:30:33"}
    return [PhotoFile(exifData0), PhotoFile(exifData1), PhotoFile(exifData2)]

def test_inferDateFromNeighboursTest2(listPhotoOneDatelessTest2):
    listOfItems:List[PhotoFile] = listPhotoOneDatelessTest2
    assert inferDateFromNeighbours(listOfItems, 1) == "1234:12:12 11:29:33+00:00"

@pytest.fixture
def listPhotoOneDatelessPreviousTest3():
    photoList = [ {"sourceFile": "fakeFile1.jpg", "EXIF:Make": "Apple", "EXIF:Model": "iPhone 8", "EXIF:CreateDate": "1234:12:12 11:22:33"},
        {"sourceFile": "fakeFile3.jpg", "EXIF:Make": "Apple", "EXIF:Model": "iPhone 8", "EXIF:CreateDate": "1234:12:12 11:30:33"},
        {"sourceFile": "fakeFile1.jpg", "EXIF:Make": "Apple", "EXIF:Model": "iPhone 8"},
        {"sourceFile": "fakeFile2.jpg", "EXIF:Make": "Apple", "EXIF:Model": "iPhone 8"},
        {"sourceFile": "fakeFile3.jpg", "EXIF:Make": "Apple", "EXIF:Model": "iPhone 8", "EXIF:CreateDate": "1234:12:12 11:40:33"}]
    return [PhotoFile(photo) for photo in photoList]

def test_inferDateFromNeighboursTest3(listPhotoOneDatelessPreviousTest3):
    listOfItems:List[PhotoFile] = listPhotoOneDatelessPreviousTest3
    assert inferDateFromNeighbours(listOfItems, 3) == "1234:12:12 11:32:33+00:00"

@pytest.fixture
def listPhotoOneDatelessPreviousTest4():
    photoList = [ {"sourceFile": "fakeFile1.jpg", "EXIF:Make": "Apple", "EXIF:Model": "iPhone 8"},
        {"sourceFile": "fakeFile3.jpg", "EXIF:Make": "Apple", "EXIF:Model": "iPhone 8"},
        {"sourceFile": "fakeFile1.jpg", "EXIF:Make": "Apple", "EXIF:Model": "iPhone 8"},
        {"sourceFile": "fakeFile2.jpg", "EXIF:Make": "Apple", "EXIF:Model": "iPhone 8"},
        {"sourceFile": "fakeFile3.jpg", "EXIF:Make": "Apple", "EXIF:Model": "iPhone 8", "EXIF:CreateDate": "1234:12:12 11:40:33"}]
    return [PhotoFile(photo) for photo in photoList]

def test_inferDateFromNeighboursTest4(listPhotoOneDatelessPreviousTest4):
    listOfItems:List[PhotoFile] = listPhotoOneDatelessPreviousTest4
    assert inferDateFromNeighbours(listOfItems, 2) == "1234:12:12 11:38:33+00:00"

@pytest.fixture
def listPhotoOneDatelessPreviousTest4():
    photoList = [ {"sourceFile": "fakeFile1.jpg", "EXIF:Make": "Apple", "EXIF:Model": "iPhone 8"},
        {"sourceFile": "fakeFile3.jpg", "EXIF:Make": "Apple", "EXIF:Model": "iPhone 8"},
        {"sourceFile": "fakeFile1.jpg", "EXIF:Make": "Apple", "EXIF:Model": "iPhone 8"},
        {"sourceFile": "fakeFile2.jpg", "EXIF:Make": "Apple", "EXIF:Model": "iPhone 8"},
        {"sourceFile": "fakeFile3.jpg", "EXIF:Make": "Apple", "EXIF:Model": "iPhone 8"}]
    return [PhotoFile(photo) for photo in photoList]

def test_inferDateFromNeighboursTest4(listPhotoOneDatelessPreviousTest4):
    listOfItems:List[PhotoFile] = listPhotoOneDatelessPreviousTest4
    assert inferDateFromNeighbours(listOfItems, 2) == None
