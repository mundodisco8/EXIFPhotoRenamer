from pytest import raises
from unittest.mock import mock_open, patch, ANY
from src.massRenamer.massRenamerClasses import *
from pathlib import Path
from json import load

# For exception checking
from json.decoder import JSONDecodeError

"""
This file contains the some stuff that is on the massRenamer module
"""

# get the path to the test file, so we can use it as base for relative paths to other files. Otherwise, paths have to be
# defined based on where YOU RUN PYTEST?
FIXTURE_DIR = Path(__file__).parent

# WARNING! Not a warning, just want to draw attention
# Description of test files, because json doesn't like commnets

# steps_generate_1.json
# One MediaFile object, without date info


def test_generateMediaFileList(mocker):
    # This is how MediaFileList should look like, with the input from the test file
    mediaFileListOut = [
        MediaFile(
            fileName=Path("/media/joel/Backup/Fotos Mac Organizadas/2018/2018-01-22 - iPhone 13.mov"),
            dateTime=None,
            source="iPhone 8",
        )
    ]

    # Mocks -
    # I don't want to write to disk
    storeMediaMock = mocker.patch("massRenamer.massRenamerClasses.storeMediaFileList")
    # And I don't want to run fixDateInteractive, I will return a date for it
    fixDateMock = mocker.patch(
        "massRenamer.massRenamerClasses.fixDateInteractive", return_value="1234:01:02 03:04:05+01:00"
    )

    generateMediaFileList(FIXTURE_DIR / "testFiles_Steps/steps_generate_1.json")

    fixDateMock.assert_called_once_with(
        0, ANY
    )  # fixDateInteractive is called once, with the only MediaFile in the list, index 0
    # assert storeMediaMock.call_args_list == []
    # print(storeMediaMock.call_args_list)
