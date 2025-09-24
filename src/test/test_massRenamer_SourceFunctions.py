from pytest import raises
from src.massRenamer.massRenamerClasses import *

"""
This file contains tests for all the methods used to find the "source" of a media file in the massRenamer module
"""

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
    assert (
        getFileSource(
            {
                "EXIF:Model": "Device X",
                "XMP:Model": "Device X",
                "Something:Model": "Device X",
                "Silly:Model": "Device X",
            }
        )
        == "Device X"
    )


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
    assert (
        getFileSource(
            {"EXIF:Make": "Brand X", "XMP:Make": "Brand X", "Something:Make": "Brand X", "Silly:Make": "Brand X"}
        )
        == "Brand X"
    )


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
