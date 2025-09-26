"""
This file contains tests for methods that either load info from files or store into into files on the massRenamer module
"""

from pytest import raises
from pytest_mock import MockerFixture

from json import loads
from json.decoder import JSONDecodeError
from pathlib import Path

from src.MassRenamer.MassRenamerClasses import (
    loadExifToolTagsFromFile,
    generateSortedMediaFileList,
    MediaFile,
    storeMediaFileListTags,
)

"""
generateSortedMediaFileList()

- Can generate a list from a file with data for a single instance
- Can generate a list from a file with data for a bunch of instances
- Can generate a list from a file with data for a bunch of instances that are not ordered
 and returns an ordered list
"""


# ExifTags_TestFile_1.json
tagsForOneInstance = [
    {
        "SourceFile": "C:/Users/mundo/OneDrive/Desktop/EXIFPhotoRenamer/FotosTest/A/028.png",
        "PNG:CreateDate": "2025-09-03T17:29:21+01:00",
        "XMP-exif:UserComment": "Screenshot",
    }
]


# Test file to test generateSortedMediaFileList(). Contains the tags of a single MediaFile object
def test_generateSortedMediaFileList_OneObject():
    ### Prepare

    ### Run Test

    mediaFileList = generateSortedMediaFileList(tagsForOneInstance)

    ### Assert
    assert mediaFileList[0].fileName == Path("C:/Users/mundo/OneDrive/Desktop/EXIFPhotoRenamer/FotosTest/A/028.png")
    assert mediaFileList[0].dateTime == "2025-09-03T17:29:21+01:00"
    assert mediaFileList[0].sidecar is None
    assert mediaFileList[0].source == "iOS Screenshot"
    assert mediaFileList[0].EXIFTags == {
        "SourceFile": "C:/Users/mundo/OneDrive/Desktop/EXIFPhotoRenamer/FotosTest/A/028.png",
        "PNG:CreateDate": "2025-09-03T17:29:21+01:00",
        "XMP-exif:UserComment": "Screenshot",
    }


# ExifTags_TestFile_2.json
# Test file to test generateSortedMediaFileList(). Contains the tags of a a bunch of MediaFile objects, and
# they are already sorted

tagsManyAndOrdered = [
    {
        "SourceFile": "C:/Users/mundo/OneDrive/Desktop/EXIFPhotoRenamer/FotosTest/A/028.png",
        "PNG:CreateDate": "2025-09-03T17:29:21+01:00",
        "XMP-exif:UserComment": "Screenshot",
    },
    {
        "SourceFile": "C:/Users/mundo/OneDrive/Desktop/EXIFPhotoRenamer/FotosTest/A/042.mov",
        "QuickTime:CreateDate": "2018-06-11T17:32:57+01:00",
        "Keys:Make": "Apple",
        "Keys:Model": "iPhone 8",
    },
    {
        "SourceFile": "C:/Users/mundo/OneDrive/Desktop/EXIFPhotoRenamer/FotosTest/A/141.png",
        "PNG:CreateDate": "2025-09-03T17:31:04+01:00",
        "XMP-exif:UserComment": "Screenshot",
    },
    {
        "SourceFile": "C:/Users/mundo/OneDrive/Desktop/EXIFPhotoRenamer/FotosTest/A/198.mp4",
        "QuickTime:CreateDate": "2018-06-12T19:10:27+01:00",
    },
    {
        "SourceFile": "C:/Users/mundo/OneDrive/Desktop/EXIFPhotoRenamer/FotosTest/A1/198.mp4",
        "QuickTime:CreateDate": "2018-06-12T19:10:27+01:00",
    },
    {
        "SourceFile": "C:/Users/mundo/OneDrive/Desktop/EXIFPhotoRenamer/FotosTest/A11/198.mp4",
        "QuickTime:CreateDate": "2018-06-12T19:10:27+01:00",
    },
]


def test_generateSortedMediaFileList_ManyOrderedObject():
    ### Prepare

    ### Run code
    mediaFileList = generateSortedMediaFileList(tagsManyAndOrdered)

    ### Assert
    # No need to check all instances, just that they are in the right order
    assert (
        mediaFileList[0].fileName.as_posix() == "C:/Users/mundo/OneDrive/Desktop/EXIFPhotoRenamer/FotosTest/A/028.png"
    )
    assert (
        mediaFileList[1].fileName.as_posix() == "C:/Users/mundo/OneDrive/Desktop/EXIFPhotoRenamer/FotosTest/A/042.mov"
    )
    assert (
        mediaFileList[2].fileName.as_posix() == "C:/Users/mundo/OneDrive/Desktop/EXIFPhotoRenamer/FotosTest/A/141.png"
    )
    assert (
        mediaFileList[3].fileName.as_posix() == "C:/Users/mundo/OneDrive/Desktop/EXIFPhotoRenamer/FotosTest/A/198.mp4"
    )
    # And mess a bit with the folder names too
    assert (
        mediaFileList[4].fileName.as_posix() == "C:/Users/mundo/OneDrive/Desktop/EXIFPhotoRenamer/FotosTest/A1/198.mp4"
    )
    assert (
        mediaFileList[5].fileName.as_posix() == "C:/Users/mundo/OneDrive/Desktop/EXIFPhotoRenamer/FotosTest/A11/198.mp4"
    )


# ExifTags_TestFile_3.json
# Test file to test generateSortedMediaFileList(). Contains the tags of a a bunch of MediaFile objects, but
# they are not sorted

tagsManyAndNotOrdered = [
    {
        "SourceFile": "C:/Users/mundo/OneDrive/Desktop/EXIFPhotoRenamer/FotosTest/A/141.png",
        "PNG:CreateDate": "2025-09-03T17:31:04+01:00",
        "XMP-exif:UserComment": "Screenshot",
    },
    {
        "SourceFile": "C:/Users/mundo/OneDrive/Desktop/EXIFPhotoRenamer/FotosTest/A11/198.mp4",
        "QuickTime:CreateDate": "2018-06-12T19:10:27+01:00",
    },
    {
        "SourceFile": "C:/Users/mundo/OneDrive/Desktop/EXIFPhotoRenamer/FotosTest/A/028.png",
        "PNG:CreateDate": "2025-09-03T17:29:21+01:00",
        "XMP-exif:UserComment": "Screenshot",
    },
    {
        "SourceFile": "C:/Users/mundo/OneDrive/Desktop/EXIFPhotoRenamer/FotosTest/A/198.mp4",
        "QuickTime:CreateDate": "2018-06-12T19:10:27+01:00",
    },
    {
        "SourceFile": "C:/Users/mundo/OneDrive/Desktop/EXIFPhotoRenamer/FotosTest/A/042.mov",
        "QuickTime:CreateDate": "2018-06-11T17:32:57+01:00",
        "Keys:Make": "Apple",
        "Keys:Model": "iPhone 8",
    },
    {
        "SourceFile": "C:/Users/mundo/OneDrive/Desktop/EXIFPhotoRenamer/FotosTest/A1/198.mp4",
        "QuickTime:CreateDate": "2018-06-12T19:10:27+01:00",
    },
]


def test_generateSortedMediaFileList_ManyNotOrderedObject():
    ### Prepare

    ### Run code
    mediaFileList = generateSortedMediaFileList(tagsManyAndNotOrdered)

    ### Assert
    # No need to check all instances, just that they are in the right order
    assert (
        mediaFileList[0].fileName.as_posix() == "C:/Users/mundo/OneDrive/Desktop/EXIFPhotoRenamer/FotosTest/A/028.png"
    )
    assert (
        mediaFileList[1].fileName.as_posix() == "C:/Users/mundo/OneDrive/Desktop/EXIFPhotoRenamer/FotosTest/A/042.mov"
    )
    assert (
        mediaFileList[2].fileName.as_posix() == "C:/Users/mundo/OneDrive/Desktop/EXIFPhotoRenamer/FotosTest/A/141.png"
    )
    assert (
        mediaFileList[3].fileName.as_posix() == "C:/Users/mundo/OneDrive/Desktop/EXIFPhotoRenamer/FotosTest/A/198.mp4"
    )
    # And mess a bit with the folder names too
    assert (
        mediaFileList[4].fileName.as_posix() == "C:/Users/mundo/OneDrive/Desktop/EXIFPhotoRenamer/FotosTest/A1/198.mp4"
    )
    assert (
        mediaFileList[5].fileName.as_posix() == "C:/Users/mundo/OneDrive/Desktop/EXIFPhotoRenamer/FotosTest/A11/198.mp4"
    )


tagsIgnoreExtension = [
    {
        "SourceFile": "/media/joel/Backup/Fotos Mac Organizadas/2018/2018-02-25 - iPhone 15.mov",
        "QuickTime:CreateDate": "2018-02-25T09:46:20",
        "QuickTime:Make": "Apple",
        "QuickTime:Model": "iPhone 8",
        "QuickTime:Software": "11.2.5",
    },
    {
        "SourceFile": "/media/joel/Backup/Fotos Mac Organizadas/2018/2018-02-25 - iPhone 15.aae",
    },
    {
        "SourceFile": "/media/joel/Backup/Fotos Mac Organizadas/2018/.ds_store",
    },
]


def test_generateSortedMediaFileList_filesWithIgnoredExtensions():
    mediaFileList = generateSortedMediaFileList(tagsIgnoreExtension)
    print(mediaFileList)
    assert len(mediaFileList) == 1


"""
loadExifToolTagsFromFile

- Load a file with two elements, check they are returned as a list of dicts
- Load a file but it doesn't contain JSON info, trhows exception
- File doesn't exist, throws exception
"""

testFileData: str = """[
{
    "SourceFile": "/media/joel/Backup/Fotos Mac Organizadas/2018/2018-02-28 - iPhone 31.mov",
    "QuickTime:CreateDate": "2018:02:28 02:25:37",
    "QuickTime:Make": "Apple",
    "QuickTime:Model": "iPhone 8",
    "QuickTime:Software": "11.2.5",
    "File:FileModifyDate": "2018:02:28 02:25:37+00:00"
},
{
    "SourceFile": "/media/joel/Backup/Fotos Mac Organizadas/2018/2018-01-22 - iPhone 13.mov",
    "QuickTime:CreateDate": "2018:01:22 11:44:37",
    "QuickTime:Make": "Apple",
    "QuickTime:Model": "iPhone 8",
    "QuickTime:Software": "11.2.2",
    "File:FileModifyDate": "2024:03:08 10:13:20+00:00"
}]"""


def test_loadExifToolTagsFromFile_success(mocker: MockerFixture):
    ### Prepare test
    # Test file is a string with tags to create two MediaFile objects
    mockFileOpen = mocker.mock_open(read_data=testFileData)  # pyright: ignore[reportUnknownMemberType]
    mocker.patch("builtins.open", mockFileOpen)

    ### Run code
    retVal = loadExifToolTagsFromFile(Path("testinput.json"))

    ### Assert
    mockFileOpen.assert_called_once_with(Path("testinput.json"), "r")
    assert retVal[0]["SourceFile"] == "/media/joel/Backup/Fotos Mac Organizadas/2018/2018-02-28 - iPhone 31.mov"
    assert retVal[1]["QuickTime:Model"] == "iPhone 8"


testFileDataNoJson: str = """some Text"""


def test_loadExifToolTagsFromFile_FileIsNotJSON(mocker: MockerFixture):
    ### Prepare test
    # Test file is a string with tags to create two MediaFile objects
    mockFileOpen = mocker.mock_open(read_data=testFileDataNoJson)  # pyright: ignore[reportUnknownMemberType]
    mocker.patch("builtins.open", mockFileOpen)

    with raises(JSONDecodeError):
        loadExifToolTagsFromFile(Path("testinput.json"))


def test_loadExifToolTagsFromFile_FileDoesntExist():
    with raises(FileNotFoundError):
        loadExifToolTagsFromFile(Path("FileThatDoesn'tExists.json"))


"""storeMediaFileListTags

- Check that what we write makes jsonsense
"""

mediaFileList = [
    MediaFile(
        Path("A.jpg"),
        None,
        {"SourceFile": "A.jpg", "QuickTime:Make": "Apple", "QuickTime:Model": "iPhone 8"},
    ),
    MediaFile(
        Path("B.jpg"),
        None,
        {"SourceFile": "B.jpg", "QuickTime:Make": "Apple", "QuickTime:Model": "iPhone 9"},
    ),
    MediaFile(
        Path("C.jpg"),
        None,
        {
            "SourceFile": "C.jpg",
            "XMP-exif:UserComment": "Screenshot",
        },
    ),
]


def test_storeMediaFileList_success(mocker: MockerFixture):
    ### Prepare test
    mockOpen = mocker.mock_open()  # pyright: ignore[reportUnknownMemberType]
    mocker.patch("builtins.open", mockOpen)

    expectedOutput = [
        '{"SourceFile": "A.jpg", "QuickTime:Make": "Apple", "QuickTime:Model": "iPhone 8"}',
        '{"SourceFile": "B.jpg", "QuickTime:Make": "Apple", "QuickTime:Model": "iPhone 9"}',
        '{"SourceFile": "C.jpg", "XMP-exif:UserComment": "Screenshot"}',
    ]

    ### Run
    storeMediaFileListTags(Path("RandomFile.txt"), mediaFileList)

    ### Assert
    mockOpen.assert_called_with(Path("RandomFile.txt"), "w")
    # the second call string is quite long, I will build it here:
    expectedBigWrite = str(expectedOutput[0]) + "," + str(expectedOutput[1]) + "," + str(expectedOutput[2])
    mockOpen().write.assert_has_calls(
        [
            mocker.call("["),
            mocker.call(expectedBigWrite),
            mocker.call("]"),
        ],
        any_order=False,
    )


class MockWriter:
    """Collect all written data."""

    def __init__(self):
        self.contents: str = ""

    def write(self, data: str) -> None:
        self.contents += data


def test_storeMediaFileList_successCheckOutput(mocker: MockerFixture):
    ### Prepare test
    mockOpen = mocker.mock_open()  # pyright: ignore[reportUnknownMemberType]
    writer = MockWriter()
    mockOpen.return_value.write = writer.write
    mocker.patch("builtins.open", mockOpen)

    ### Run
    storeMediaFileListTags(Path("RandomFile.txt"), mediaFileList)

    ### Assert
    # get stuff written to the file, is stored in writer.contents
    # Check it is parseable json
    loads(writer.contents)
