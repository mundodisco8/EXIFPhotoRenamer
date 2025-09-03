from pytest import raises
from unittest.mock import mock_open, patch
from src.massRenamer.massRenamerClasses import *
from pathlib import Path

# For exception checking
from json.decoder import JSONDecodeError

"""
This file contains tests for methods that either load info from files or store into into files on the massRenamer module
"""

# get the path to the test file, so we can use it as base for relative paths to other files. Otherwise, paths have to be
# defined based on where YOU RUN PYTEST?
FIXTURE_DIR = Path(__file__).parent

# WARNING! Not a warning, just want to draw attention
# Description of test files, because json doesn't like commnets

# ExifTags_TestFile_1.json
# A single dictionary for a single file, with its EXIF tags. All tags presents to create a MediaFile Object

# ExifTags_TestFile_2.json
# A bunch of dictionaries for a multiple files, with their EXIF tags. All tags presents to create a MediaFile Objects. Files are sorted

# ExifTags_TestFile_3.json
# A bunch of dictionaries for a multiple files, with their EXIF tags. All tags presents to create a MediaFile Objects. Files are NOT sorted

"""
generateSortedMediaFileList()

- Can generate a list from a file with data for a single instance
- Can generate a list from a file with data for a bunch of instances
- Can generate a list from a file with data for a bunch of instances that are not ordered
 and returns an ordered list
"""


# ExifTags_TestFile_1.json
# Test file to test generateSortedMediaFileList(). Contains the tags of a single MediaFile object
def test_generateSortedMediaFileList_OneObject():
    etData: List[Dict[str, str]]
    with open(FIXTURE_DIR / Path("supportFiles/ExifTags_TestFile_1.json"), "r") as readFile:
        etData = load(readFile)
    mediaFileList = generateSortedMediaFileList(etData)
    assert mediaFileList[0]._fileName == Path(
        "/media/joel/Backup/Fotos Mac Organizadas/2018/2018-02-25 - iPhone 15.mov"
    )
    assert mediaFileList[0]._dateTime == "2018:02:25 09:46:20+00:00"
    assert mediaFileList[0]._sidecar == None
    assert mediaFileList[0]._source == "iPhone 8"


# ExifTags_TestFile_2.json
# Test file to test generateSortedMediaFileList(). Contains the tags of a a bunch of MediaFile objects, and
# they are already sorted
def test_generateSortedMediaFileList_ManyOrderedObject():
    etData: List[Dict[str, str]]
    with open(FIXTURE_DIR / Path("supportFiles/ExifTags_TestFile_2.json"), "r") as readFile:
        etData = load(readFile)
    mediaFileList = generateSortedMediaFileList(etData)

    assert (
        mediaFileList[0].getFileName().as_posix()
        == "/media/joel/Backup/Fotos Mac Organizadas/2018/2018-01-22 - iPhone 13.mov"
    )
    assert (
        mediaFileList[1].getFileName().as_posix()
        == "/media/joel/Backup/Fotos Mac Organizadas/2018/2018-02-25 - iPhone 15.mov"
    )
    assert (
        mediaFileList[2].getFileName().as_posix()
        == "/media/joel/Backup/Fotos Mac Organizadas/2018/2018-02-28 - iPhone 31.mov"
    )
    assert (
        mediaFileList[3].getFileName().as_posix()
        == "/media/joel/Backup/Fotos Mac Organizadas/2018/2018-03-30 - iPhone 13.heic"
    )
    assert (
        mediaFileList[4].getFileName().as_posix()
        == "/media/joel/Backup/Fotos Mac Organizadas/2018/2018-12-25 - iPhone 50.mov"
    )
    assert (
        mediaFileList[5].getFileName().as_posix()
        == "/media/joel/Backup/Fotos Mac Organizadas/2018/2019-02-10 - iPhone 094.mov"
    )


# ExifTags_TestFile_3.json
# Test file to test generateSortedMediaFileList(). Contains the tags of a a bunch of MediaFile objects, but
# they are not sorted
def test_generateSortedMediaFileList_ManyNotOrderedObject():
    etData: List[Dict[str, str]]
    with open(FIXTURE_DIR / Path("supportFiles/ExifTags_TestFile_3.json"), "r") as readFile:
        etData = load(readFile)
    mediaFileList = generateSortedMediaFileList(etData)

    assert (
        mediaFileList[0].getFileName().as_posix()
        == "/media/joel/Backup/Fotos Mac Organizadas/2018/2018-01-22 - iPhone 13.mov"
    )
    assert (
        mediaFileList[1].getFileName().as_posix()
        == "/media/joel/Backup/Fotos Mac Organizadas/2018/2018-02-25 - iPhone 15.mov"
    )
    assert (
        mediaFileList[2].getFileName().as_posix()
        == "/media/joel/Backup/Fotos Mac Organizadas/2018/2018-02-28 - iPhone 31.mov"
    )
    assert (
        mediaFileList[3].getFileName().as_posix()
        == "/media/joel/Backup/Fotos Mac Organizadas/2018/2018-03-30 - iPhone 13.heic"
    )
    assert (
        mediaFileList[4].getFileName().as_posix()
        == "/media/joel/Backup/Fotos Mac Organizadas/2018/2018-12-25 - iPhone 50.mov"
    )
    assert (
        mediaFileList[5].getFileName().as_posix()
        == "/media/joel/Backup/Fotos Mac Organizadas/2018/2019-02-10 - iPhone 094.mov"
    )


def test_generateSortedMediaFileList_filesWithIgnoredExtensions():
    data = """[
    {
        "SourceFile": "/media/joel/Backup/Fotos Mac Organizadas/2018/2018-02-25 - iPhone 15.mov",
        "QuickTime:CreateDate": "2018:02:25 09:46:20",
        "QuickTime:Make": "Apple",
        "QuickTime:Model": "iPhone 8",
        "QuickTime:Software": "11.2.5",
        "File:FileModifyDate": "2018:02:25 09:46:19+00:00"
    },
    {
        "SourceFile": "/media/joel/Backup/Fotos Mac Organizadas/2018/2018-02-25 - iPhone 15.aae",
    },
    {
        "SourceFile": "/media/joel/Backup/Fotos Mac Organizadas/2018/.ds_store",
    }
        ]"""
    etData: List[Dict[str, str]] = eval(data)
    mediaFileList = generateSortedMediaFileList(etData)
    print(mediaFileList)
    assert len(mediaFileList) == 1


"""
loadMediaFileListFromFile

- Load a file with two elements, check they are returned as a list of MediaFile
- Load a file but it contains a list of any other stuff, other than MediaFile, trhows exception
- Load a file but contents are not evaluable, trhows exception
- File doesn't exist, throws exception
"""


def test_loadMediaFileListFromFile_success():
    # Test file is a string with two MediaFile objects
    testFileData: str = '[MediaFile(fileName=Path("/media/joel/Backup/Fotos Mac Organizadas/2018/2018-01-22 - iPhone 13.mov"), dateTime="2018:01:22 11:44:37+00:00", source="iPhone 8"), MediaFile(fileName=Path("/media/joel/Backup/Fotos Mac Organizadas/2018/2018-02-25 - iPhone 15.mov"), dateTime="2018:02:25 09:46:20+00:00", source="iPhone 8")]'

    mock = mock_open(read_data=testFileData)
    with patch("builtins.open", mock):
        retVal = loadMediaFileListFromFile(Path("testinput.txt"))

    mock.assert_called_once_with(Path("testinput.txt"), "r")
    assert retVal[0].getFileName() == Path("/media/joel/Backup/Fotos Mac Organizadas/2018/2018-01-22 - iPhone 13.mov")
    assert retVal[1].getTime() == "2018:02:25 09:46:20+00:00"


def test_loadMediaFileListFromFile_FileIsListButNotMediaFile():
    # Test file is a string with tags to create two MediaFile objects
    testFileData: str = "[1, 2, 3, 4]"

    mock = mock_open(read_data=testFileData)
    with patch("builtins.open", mock):
        with raises(TypeError) as excinfo:
            loadMediaFileListFromFile(Path("testinput.txt"))


def test_loadMediaFileListFromFile_FileIsNotEvaluable():
    # Test file is a string with tags to create two MediaFile objects
    testFileData: str = """some Text"""

    mock = mock_open(read_data=testFileData)
    with patch("builtins.open", mock):
        with raises(SyntaxError) as excinfo:
            loadMediaFileListFromFile(Path("testinput.txt"))


def test_loadMediaFileListFromFile_FileDoesntExist():
    with raises(FileNotFoundError) as excinfo:
        loadMediaFileListFromFile(Path("FileThatDoesn'tExists.txt"))


"""
storeMediaFileList

- Store a list of MediaFile objects to a file
"""


def test_storeMediaFileList_success():
    # Test file is a string with tags to create two MediaFile objects
    listMediaFiles: List[MediaFile] = eval(
        '[MediaFile(fileName=Path("/media/joel/Backup/Fotos Mac Organizadas/2018/2018-01-22 - iPhone 13.mov"), dateTime="2018:01:22 11:44:37+00:00", source="iPhone 8"), MediaFile(fileName=Path("/media/joel/Backup/Fotos Mac Organizadas/2018/2018-02-25 - iPhone 15.mov"), dateTime="2018:02:25 09:46:20+00:00", source="iPhone 8")]'
    )

    mock = mock_open()
    with patch("builtins.open", mock):
        storeMediaFileList(Path("testoutput.json"), listMediaFiles)

    mock.assert_called_once_with(Path("testoutput.json"), "w")
    mock().write.assert_called_once_with(str(listMediaFiles))


"""
loadExifToolTagsFromFile

- Load a file with two elements, check they are returned as a list of dicts
- Load a file but it doesn't contain JSON info, trhows exception
- File doesn't exist, throws exception
"""


def test_loadExifToolTagsFromFile_success():
    # Test file is a string with tags to create two MediaFile objects
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

    mock = mock_open(read_data=testFileData)
    with patch("builtins.open", mock):
        retVal = loadExifToolTagsFromFile(Path("testinput.json"))

    mock.assert_called_once_with(Path("testinput.json"), "r")
    assert retVal[0]["SourceFile"] == "/media/joel/Backup/Fotos Mac Organizadas/2018/2018-02-28 - iPhone 31.mov"
    assert retVal[1]["QuickTime:Model"] == "iPhone 8"


def test_loadExifToolTagsFromFile_FileIsNotJSON():
    # Test file is a string with tags to create two MediaFile objects
    testFileData: str = """some Text"""

    mock = mock_open(read_data=testFileData)
    with patch("builtins.open", mock):
        with raises(JSONDecodeError) as excinfo:
            loadExifToolTagsFromFile(Path("testinput.json"))


def test_loadExifToolTagsFromFile_FileDoesntExist():
    with raises(FileNotFoundError) as excinfo:
        loadExifToolTagsFromFile(Path("FileThatDoesn'tExists.json"))


"""
storeExifToolTagsFromFile

- Store some ExifTool tags, given as a list of dictionaries, in a file
"""


def test_storeExifToolTags_success():
    # Test file is a string with tags to create two MediaFile objects
    tagsToWrite: List[Dict[str, str]] = [
        {
            "SourceFile": "/media/joel/Backup/Fotos Mac Organizadas/2018/2018-02-28 - iPhone 31.mov",
            "QuickTime:CreateDate": "2018:02:28 02:25:37",
            "QuickTime:Make": "Apple",
            "QuickTime:Model": "iPhone 8",
            "QuickTime:Software": "11.2.5",
            "File:FileModifyDate": "2018:02:28 02:25:37+00:00",
        },
        {
            "SourceFile": "/media/joel/Backup/Fotos Mac Organizadas/2018/2018-01-22 - iPhone 13.mov",
            "QuickTime:CreateDate": "2018:01:22 11:44:37",
            "QuickTime:Make": "Apple",
            "QuickTime:Model": "iPhone 8",
            "QuickTime:Software": "11.2.2",
            "File:FileModifyDate": "2024:03:08 10:13:20+00:00",
        },
    ]

    mock = mock_open()
    with patch("builtins.open", mock):
        storeExifToolTags(Path("testoutput.json"), tagsToWrite)

    mock.assert_called_once_with(Path("testoutput.json"), "w")
    mock().write.assert_called_once_with(str(tagsToWrite))
