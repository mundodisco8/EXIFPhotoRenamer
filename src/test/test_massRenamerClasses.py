from pathlib import Path

from pytest import MonkeyPatch

from src.MassRenamer.MassRenamerClasses import MediaFile

"""
MediaFile.fromExifTags Class test:
- Creation
- repr method prints the data in the correct format (so we can init more instances of the MediaFile class out of it)
"""


def test_MediaFile_Creation():
    exifData = {
        "SourceFile": "fakeFile.jpg",
        "IFD0:Make": "Apple",
        "IFD0:Model": "iPhone 8",
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
        "IFD0:Make": "Apple",
        "IFD0:Model": "iPhone 8",
        "ExifIFD:CreateDate": "1234-12-12T11:22:33",
    }
    sourceInstance = MediaFile.fromExifTags(exifData)
    print(sourceInstance.__repr__())
    testInstance = eval(sourceInstance.__repr__())
    assert isinstance(testInstance, type(sourceInstance))
    assert testInstance.fileName == Path("fakeFile.jpg")
    assert testInstance.dateTime == "1234-12-12T11:22:33+00:00"
    assert testInstance.sidecar is None
    assert testInstance.source == "iPhone 8"
    assert testInstance.EXIFTags == exifData


"""
Get Sources:

"""


# A file with maker and model
def test_getSources_Success():
    ### Prepare
    mediaFile = MediaFile(Path("A.jpg"), "2025-10-10T08:01:02+00:00", {"IFD0:Make": "MyMaker", "IFD0:Model": "MyModel"})
    expectedSource = "MyMaker MyModel"

    ### Run
    source = mediaFile.getFileSource()

    ### Assert
    assert expectedSource == source


# An iPhone file just returns the model
def test_getSources_Apple():
    ### Prepare
    mediaFile = MediaFile(
        Path("A.jpg"), "2025-10-10T08:01:02+00:00", {"IFD0:Make": "Apple", "IFD0:Model": "iPhone 13 mini"}
    )
    expectedSource = "iPhone 13 mini"

    ### Run
    source = mediaFile.getFileSource()

    ### Assert
    assert expectedSource == source


# A Google file just returns the model, too
def test_getSources_Google():
    ### Prepare
    mediaFile = MediaFile(Path("A.jpg"), "2025-10-10T08:01:02+00:00", {"IFD0:Make": "Google", "IFD0:Model": "Pixel 7"})
    expectedSource = "Pixel 7"

    ### Run
    source = mediaFile.getFileSource()

    ### Assert
    assert expectedSource == source


# A Google file just returns the model, too
def test_getSources_Olympus():
    ### Prepare
    mediaFile = MediaFile(
        Path("A.jpg"), "2025-10-10T08:01:02+00:00", {"IFD0:Make": "OLYMPUS IMAGING CORP.", "IFD0:Model": "ABC"}
    )
    expectedSource = "Olympus ABC"

    ### Run
    source = mediaFile.getFileSource()

    ### Assert
    assert expectedSource == source


# Test quicktime files, that have their make/model in the "keys" group
# A Quicktime file will probably come from Apple, but here, check make and model
def test_getSources_Quicktime():
    ### Prepare
    mediaFile = MediaFile(Path("A.jpg"), "2025-10-10T08:01:02+00:00", {"Keys:Make": "MyMaker", "Keys:Model": "MyModel"})
    expectedSource = "MyMaker MyModel"

    ### Run
    source = mediaFile.getFileSource()

    ### Assert
    assert expectedSource == source


# Screenshots are tagged as such in the User Comments tag ("XMP-exif:UserComment") at least in iPhones
def test_getSources_screenshot():
    ### Prepare
    mediaFile = MediaFile(Path("A.jpg"), "2025-10-10T08:01:02+00:00", {"XMP-exif:UserComment": "Screenshot"})
    expectedSource = "iOS Screenshot"

    ### Run
    source = mediaFile.getFileSource()

    ### Assert
    assert expectedSource == source


# Instagram pics
def test_getSources_Instagram():
    ### Prepare
    mediaFile = MediaFile(Path("A.jpg"), "2025-10-10T08:01:02+00:00", {"XMP:Software": "Something Something Instagram"})
    expectedSource = "Instagram"

    mediaFile2 = MediaFile(Path("A.jpg"), "2025-10-10T08:01:02+00:00", {"XMP:Software": "Facebook This or The Other"})
    expectedSource2 = "Instagram"

    ### Run
    source = mediaFile.getFileSource()
    source2 = mediaFile2.getFileSource()

    ### Assert
    assert expectedSource == source
    assert expectedSource2 == source2


# Screenshots are tagged as such in the User Comments tag ("XMP-exif:UserComment") at least in iPhones
def test_getSources_PicsArt():
    ### Prepare
    mediaFile = MediaFile(Path("A.jpg"), "2025-10-10T08:01:02+00:00", {"IFD0:Software": "PicsArt"})
    expectedSource = "PicsArt"

    ### Run
    source = mediaFile.getFileSource()

    ### Assert
    assert expectedSource == source


# Now check that the order for the sources rules is followed:
# 1. Make And Model
# 2. iOS Screenshots
# 3. Instagram
# 4. PicsArt
# 5. Photoshop
# Then Whatsapp
def test_getSources_testPrecedenceOrder():
    ### Prepare
    mediaFile1 = MediaFile(
        Path("A.jpg"),
        "2025-10-10T08:01:02+00:00",
        {
            "IFD0:Make": "MyMaker",
            "IFD0:Model": "MyModel",
            "Keys:Make": "QuickTimeMaker",
            "Keys:Model": "QuicktimeModel",
            "XMP-exif:UserComment": "Screenshot",
            "XMP:Software": "Something Something Instagram",
            "IFD0:Software": "PicsArt",
        },
    )
    mediaFile2 = MediaFile(
        Path("A.jpg"),
        "2025-10-10T08:01:02+00:00",
        {
            "Keys:Make": "QuickTimeMaker",
            "Keys:Model": "QuicktimeModel",
            "XMP-exif:UserComment": "Screenshot",
            "XMP:Software": "Something Something Instagram",
            "IFD0:Software": "PicsArt",
        },
    )
    mediaFile3 = MediaFile(
        Path("A.jpg"),
        "2025-10-10T08:01:02+00:00",
        {
            "XMP-exif:UserComment": "Screenshot",
            "XMP:Software": "Something Something Instagram",
            "IFD0:Software": "PicsArt",
        },
    )
    mediaFile4 = MediaFile(
        Path("A.jpg"),
        "2025-10-10T08:01:02+00:00",
        {
            "XMP:Software": "Something Something Instagram",
            "IFD0:Software": "PicsArt",
        },
    )
    mediaFile5 = MediaFile(
        Path("A.jpg"),
        "2025-10-10T08:01:02+00:00",
        {
            "IFD0:Software": "PicsArt",
        },
    )
    mediaFile6 = MediaFile(
        Path("A.jpg"),
        "2025-10-10T08:01:02+00:00",
        {},
    )
    expectedSource1 = "MyMaker MyModel"
    expectedSource2 = "QuickTimeMaker QuicktimeModel"
    expectedSource3 = "iOS Screenshot"
    expectedSource4 = "Instagram"
    expectedSource5 = "PicsArt"
    expectedSource6 = "WhatsApp"

    ### Run
    source1 = mediaFile1.getFileSource()
    source2 = mediaFile2.getFileSource()
    source3 = mediaFile3.getFileSource()
    source4 = mediaFile4.getFileSource()
    source5 = mediaFile5.getFileSource()
    source6 = mediaFile6.getFileSource()

    ### Assert
    assert expectedSource1 == source1
    assert expectedSource2 == source2
    assert expectedSource3 == source3
    assert expectedSource4 == source4
    assert expectedSource5 == source5
    assert expectedSource6 == source6


"""
getSidecar

- File has a sidecar, with same name, and aae extension
- File has a sidecar, with same name plus O suffix, and aae extension
- File doesn't have a sidecar

"""


def test_getSidecar_sidecarWithSameName():
    ### Prepare
    mediaFile = MediaFile(
        Path("sidecarExists.jpg"),
        "2025-10-10T08:01:02+00:00",
        {
            "IFD0:Make": "MyMaker",
            "IFD0:Model": "MyModel",
        },
    )
    monkeypatch = MonkeyPatch()

    def mocked_is_file(self: Path):
        if self.name == "sidecarExists.aae":
            return True
        else:
            return False

    monkeypatch.setattr(Path, "is_file", mocked_is_file)

    expectedSideCarPath = Path("sidecarExists.aae")

    ### Run
    sidecarPath = mediaFile.findSidecar()

    ### Assert
    assert expectedSideCarPath == sidecarPath


def test_getSidecar_sidecarWithOSuffix():
    ### Prepare
    mediaFile = MediaFile(
        Path("sidecarExists.jpg"),
        "2025-10-10T08:01:02+00:00",
        {
            "IFD0:Make": "MyMaker",
            "IFD0:Model": "MyModel",
        },
    )
    monkeypatch = MonkeyPatch()

    def mocked_is_file(self: Path):
        if self.name == "sidecarExistsO.aae":
            return True
        else:
            return False

    monkeypatch.setattr(Path, "is_file", mocked_is_file)

    expectedSideCarPath = Path("sidecarExistsO.aae")

    ### Run
    sidecarPath = mediaFile.findSidecar()

    ### Assert
    assert expectedSideCarPath == sidecarPath


def test_getSidecar_sidecarDoesntExist():
    ### Prepare
    mediaFile = MediaFile(
        Path("sidecarDoesNotExists.jpg"),
        "2025-10-10T08:01:02+00:00",
        {
            "IFD0:Make": "MyMaker",
            "IFD0:Model": "MyModel",
        },
    )
    monkeypatch = MonkeyPatch()

    def mocked_is_file(self: Path):
        return False

    monkeypatch.setattr(Path, "is_file", mocked_is_file)

    expectedSideCarPath = None

    ### Run
    sidecarPath = mediaFile.findSidecar()

    ### Assert
    assert expectedSideCarPath == sidecarPath
