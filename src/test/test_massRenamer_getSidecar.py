from pytest import MonkeyPatch
from pathlib import Path

from src.massRenamer.massRenamerClasses import getSidecar

"""
getSidecar

- File has a sidecar, with same name, and aae extension
- File has a sidecar, with same name plus O suffix, and aae extension
- File doesn't have a sidecar

"""


def test_getSidecar_sidecarSameName():
    monkeypatch = MonkeyPatch()

    def mocked_is_file(self):
        if self.name == "sidecarExists.aae":
            return True
        else:
            return False

    monkeypatch.setattr(Path, "is_file", mocked_is_file)

    testPathExists = Path("sidecarExists.jpg")
    assert getSidecar(testPathExists) == Path("sidecarExists.aae")


def test_getSidecar_sidecarWithOSuffix():
    monkeypatch = MonkeyPatch()

    def mocked_is_file(self):
        if self.name == "sidecarExistsO.aae":
            return True
        else:
            return False

    monkeypatch.setattr(Path, "is_file", mocked_is_file)

    testPathExists = Path("sidecarExists.jpg")
    assert getSidecar(testPathExists) == Path("sidecarExistsO.aae")


def test_getSidecar_sidecarDoesntExist():
    monkeypatch = MonkeyPatch()

    def mocked_is_file(self):
        return False

    monkeypatch.setattr(Path, "is_file", mocked_is_file)

    testPathExists = Path("sidecarDoesntExists.jpg")
    assert getSidecar(testPathExists) == None
