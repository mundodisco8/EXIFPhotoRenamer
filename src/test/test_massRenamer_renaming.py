from pathlib import Path

from src.MassRenamer.MassRenamerClasses import MediaFile, findNewNames

"""
Renamer Algorithm

"""


def test_rename_SuccessOneFile():
    """Testing with one single file"""
    ### Prepare
    testMediaFileList = [
        MediaFile(Path("MyFile.jpg"), "2025-01-02T01:02:03+00:00", {"IFD0:Make": "MyMaker", "IFD0:Model": "MyModel"})
    ]
    expectedNewName = Path("test/2025/MyMaker MyModel/2025-01-02 MyMaker MyModel 1.jpg")

    ### Run
    findNewNames(testMediaFileList, Path("test"))

    ### Assert
    assert expectedNewName == testMediaFileList[0].newName


def test_rename_SuccessManyFilesWithSameDay():
    """Test with some more files, check that we insert a 0 in the first 9 files 1-9 -> 01-09"""
    ### Prepare
    # Python trap! this creates an array with 150 references to the same object!!!
    # testMediaFileList = [
    #     MediaFile(Path("MyFile.jpg"), "2025-01-02T01:02:03+00:00", {"IFD0:Make": "MyMaker", "IFD0:Model": "MyModel"}),
    # ] * 150
    # This is the way to do it
    testMediaFileList = [
        MediaFile(Path("MyFile.jpg"), "2025-01-02T01:02:03+00:00", {"IFD0:Make": "MyMaker", "IFD0:Model": "MyModel"})
        for _ in range(150)
    ]

    expectedNewNames0 = Path("test/2025/MyMaker MyModel/2025-01-02 MyMaker MyModel 001.jpg")
    expectedNewNames136 = Path("test/2025/MyMaker MyModel/2025-01-02 MyMaker MyModel 137.jpg")
    expectedNewNameLast = Path("test/2025/MyMaker MyModel/2025-01-02 MyMaker MyModel 150.jpg")

    ### Run
    findNewNames(testMediaFileList, Path("test"))

    ### Assert
    assert expectedNewNames0 == testMediaFileList[0].newName
    assert expectedNewNames136 == testMediaFileList[136].newName
    assert expectedNewNameLast == testMediaFileList[-1].newName


def test_rename_SuccessManyFilesWithSameDay_SkipNoDates():
    """Test multiple files, but some of them must be skipped as they don't have a date"""
    ### Prepare
    # Python trap! this creates an array with 150 references to the same object!!!
    # testMediaFileList = [
    #     MediaFile(Path("MyFile.jpg"), "2025-01-02T01:02:03+00:00", {"IFD0:Make": "MyMaker", "IFD0:Model": "MyModel"}),
    # ] * 150
    # This is the way to do it
    testMediaFileList = [
        MediaFile(Path("MyFile.jpg"), "2025-01-02T01:02:03+00:00", {"IFD0:Make": "MyMaker", "IFD0:Model": "MyModel"}),
        MediaFile(Path("MyFile.jpg"), None, {"IFD0:Make": "MyMaker", "IFD0:Model": "MyModel"}),
        MediaFile(Path("MyFile.jpg"), "2025-01-02T01:02:03+00:00", {"IFD0:Make": "MyMaker", "IFD0:Model": "MyModel"}),
        MediaFile(Path("MyFile.jpg"), None, {"IFD0:Make": "MyMaker", "IFD0:Model": "MyModel"}),
        MediaFile(Path("MyFile.jpg"), "2025-01-02T01:02:03+00:00", {"IFD0:Make": "MyMaker", "IFD0:Model": "MyModel"}),
    ]

    expectedNewName0 = Path("test/2025/MyMaker MyModel/2025-01-02 MyMaker MyModel 1.jpg")
    expectedNewName1 = None
    expectedNewName2 = Path("test/2025/MyMaker MyModel/2025-01-02 MyMaker MyModel 2.jpg")
    expectedNewName3 = None
    expectedNewName4 = Path("test/2025/MyMaker MyModel/2025-01-02 MyMaker MyModel 3.jpg")

    ### Run
    findNewNames(testMediaFileList, Path("test"))

    ### Assert
    assert expectedNewName0 == testMediaFileList[0].newName
    assert expectedNewName1 == testMediaFileList[1].newName
    assert expectedNewName2 == testMediaFileList[2].newName
    assert expectedNewName3 == testMediaFileList[3].newName
    assert expectedNewName4 == testMediaFileList[4].newName


def test_rename_SuccessManyFilesWithSameDay_RelocateToSameFolder():
    """Test with files that share a source, but are located in different folders.

    The files will be relocated to a common folder with the source name
    """
    ### Prepare
    # Python trap! this creates an array with 150 references to the same object!!!
    # testMediaFileList = [
    #     MediaFile(Path("MyFile.jpg"), "2025-01-02T01:02:03+00:00", {"IFD0:Make": "MyMaker", "IFD0:Model": "MyModel"}),
    # ] * 150
    # This is the way to do it
    testMediaFileList = [
        MediaFile(Path("A/MyFile.jpg"), "2025-01-02T01:02:03+00:00", {"IFD0:Make": "MyMaker", "IFD0:Model": "MyModel"}),
        MediaFile(Path("B/MyFile.jpg"), "2025-01-02T01:02:03+00:00", {"IFD0:Make": "MyMaker", "IFD0:Model": "MyModel"}),
        MediaFile(Path("C/MyFile.jpg"), "2025-01-02T01:02:03+00:00", {"IFD0:Make": "MyMaker", "IFD0:Model": "MyModel"}),
        MediaFile(Path("D/MyFile.jpg"), "2025-01-02T01:02:03+00:00", {"IFD0:Make": "MyMaker", "IFD0:Model": "MyModel"}),
        MediaFile(Path("E/MyFile.jpg"), "2025-01-02T01:02:03+00:00", {"IFD0:Make": "MyMaker", "IFD0:Model": "MyModel"}),
    ]

    expectedNewName0 = Path("test/2025/MyMaker MyModel/2025-01-02 MyMaker MyModel 1.jpg")
    expectedNewName1 = Path("test/2025/MyMaker MyModel/2025-01-02 MyMaker MyModel 2.jpg")
    expectedNewName2 = Path("test/2025/MyMaker MyModel/2025-01-02 MyMaker MyModel 3.jpg")
    expectedNewName3 = Path("test/2025/MyMaker MyModel/2025-01-02 MyMaker MyModel 4.jpg")
    expectedNewName4 = Path("test/2025/MyMaker MyModel/2025-01-02 MyMaker MyModel 5.jpg")

    ### Run
    findNewNames(testMediaFileList, Path("test"))

    ### Assert
    assert expectedNewName0 == testMediaFileList[0].newName
    assert Path("A/MyFile.jpg") == testMediaFileList[0].fileName
    assert expectedNewName1 == testMediaFileList[1].newName
    assert expectedNewName2 == testMediaFileList[2].newName
    assert expectedNewName3 == testMediaFileList[3].newName
    assert expectedNewName4 == testMediaFileList[4].newName
    assert Path("E/MyFile.jpg") == testMediaFileList[4].fileName


def test_rename_differentSources():
    """Files from different sources get sorted together, stored in a folder with the source name"""
    ### Prepare
    testMediaFileMyMaker = [
        MediaFile(Path("MyFile.jpg"), "2025-01-02T01:02:03+00:00", {"IFD0:Make": "MyMaker", "IFD0:Model": "MyModel"})
        for _ in range(150)
    ]
    testMediaFileScreenshot = [
        MediaFile(Path("MyFile.jpg"), "2025-01-02T01:02:03+00:00", {"XMP-exif:UserComment": "Screenshot"})
        for _ in range(150)
    ]
    testMediaFileList = testMediaFileMyMaker + testMediaFileScreenshot
    expectedName0 = Path("test/2025/MyMaker MyModel/2025-01-02 MyMaker MyModel 001.jpg")
    expectedName14 = Path("test/2025/MyMaker MyModel/2025-01-02 MyMaker MyModel 015.jpg")
    expectedNameFirstScreenShot = Path("test/2025/iOS Screenshot/2025-01-02 iOS Screenshot 001.jpg")
    expectedNameLast = Path("test/2025/iOS Screenshot/2025-01-02 iOS Screenshot 150.jpg")

    ### Run
    findNewNames(testMediaFileList, Path("test"))

    ### Assert
    assert expectedName0 == testMediaFileList[0].newName
    assert expectedName14 == testMediaFileList[14].newName
    assert expectedNameFirstScreenShot == testMediaFileList[len(testMediaFileMyMaker)].newName
    assert expectedNameLast == testMediaFileList[-1].newName
