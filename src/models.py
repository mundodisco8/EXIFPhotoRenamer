from enum import StrEnum

from PySide6.QtCore import Qt, QAbstractListModel, QAbstractTableModel, QModelIndex, QPersistentModelIndex
from PySide6.QtGui import QColor, QFont

from massRenamer.massRenamerClasses import MediaFile, isTagATimeTag


class SunnyBeach(StrEnum):
    # Sunny Beach Day Palette
    blue = "#70a7bd"
    teal = "#7bdcd0"
    yellow = "#f3dfaf"
    orange = "#f9cdaa"
    darkOrange = "#f2b2a2"


class toRenameModel(QAbstractTableModel):
    """A model to show renameable files and their proposed new names

    Args:
        QAbstractTableModel (_type_): ???
    """

    def __init__(self, mediaFileList: list[MediaFile] | None = None) -> None:
        """Inits the class

        Args:
            datelessItemsList (list[tuple[str,str]] | None, optional): A list of files that can be renamed and their
            proposed new name.
            Defaults to None.
        """
        self.columns = ["Current Filename", "Proposed New Name"]
        super().__init__()

        self.toRenameList: list[tuple[str, str]] = []
        if mediaFileList:
            for instance in mediaFileList:
                if instance.newName:
                    self.toRenameList.append((str(instance.fileName), str(instance.newName)))

    def data(self, index: QModelIndex | QPersistentModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> str | None:
        if role == Qt.ItemDataRole.DisplayRole:
            return self.toRenameList[index.row()][index.column()]
        # TODO: If has sidecar, paint background?
        return None

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.ItemDataRole.DisplayRole):
        # for setting columns name
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return f"{self.columns[section]}"

    def rowCount(self, parent: QModelIndex | QPersistentModelIndex = QModelIndex()) -> int:
        return len(self.toRenameList)

    def columnCount(self, parent: QModelIndex | QPersistentModelIndex = QModelIndex()) -> int:
        return 2

    def replaceListOfFiles(self, mediaFileList: list[MediaFile]) -> None:
        self.toRenameList = []
        for instance in mediaFileList:
            if instance.newName:
                self.toRenameList.append((str(instance.fileName), str(instance.newName)))
        self.layoutChanged.emit()


class showDatelessModel(QAbstractTableModel):
    """A model for the dateless items table

    Args:
        QAbstractTableModel (_type_): ???
    """

    def __init__(self, mediaFileList: list[MediaFile] | None = None) -> None:
        """Inits the class

        Args:
            datelessItemsList (list[tuple[str,str]] | None, optional): A list of files that don't have a clear date.
            Defaults to None.
        """

        self.columns = ["Filename", "Proposed New Date"]
        super().__init__()
        self.datelessItemsList: list[tuple[str, str]] = []
        if mediaFileList:
            for instance in mediaFileList:
                if not instance.dateTime:
                    self.datelessItemsList.append((str(instance.fileName), ""))

    def data(self, index: QModelIndex | QPersistentModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> str | None:
        if role == Qt.ItemDataRole.DisplayRole:
            return self.datelessItemsList[index.row()][index.column()]
        return None

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.ItemDataRole.DisplayRole):
        # for setting columns name
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return f"{self.columns[section]}"

    def rowCount(self, parent: QModelIndex | QPersistentModelIndex = QModelIndex()) -> int:
        return len(self.datelessItemsList)

    def columnCount(self, parent: QModelIndex | QPersistentModelIndex = QModelIndex()) -> int:
        return 2

    def replaceListOfFiles(self, mediaFileList: list[MediaFile]) -> None:
        self.datelessItemsList = []
        for instance in mediaFileList:
            if not instance.dateTime:
                self.datelessItemsList.append((str(instance.fileName), ""))

        self.layoutChanged.emit()


# TODO: Change name!
class fixDateModel(QAbstractTableModel):
    """A Model for the table that presents the date tags of a dateless item

    Args:
        QAbstractTableModel (_type_): ???
    """

    def __init__(self, mediaFile: MediaFile | None = None) -> None:
        super().__init__()
        self.dateTagList: list[tuple[str, str]] = []
        if mediaFile and mediaFile.EXIFTags:  # if the dict has tags
            # Show the date tags for this file
            for tag in mediaFile.EXIFTags:
                if isTagATimeTag(tag):
                    self.dateTagList.append((tag, mediaFile.EXIFTags[tag]))

    def data(
        self, index: QModelIndex | QPersistentModelIndex, role: int = Qt.ItemDataRole.DisplayRole
    ) -> str | QColor | QFont | None:
        if role == Qt.ItemDataRole.DisplayRole:
            return self.dateTagList[index.row()][index.column()]
        elif role == Qt.ItemDataRole.BackgroundRole:
            # Get some background colours to distinghuis tags?
            if self.dateTagList[index.row()][0].startswith("System"):
                return QColor(SunnyBeach.darkOrange)
            if self.dateTagList[index.row()][0].startswith("Exif"):
                return QColor(SunnyBeach.orange)
            if self.dateTagList[index.row()][0].startswith("Inferred"):
                return QColor(SunnyBeach.yellow)
            else:
                return QColor(SunnyBeach.teal)
        elif role == Qt.ItemDataRole.FontRole and index.column() == 1:
            myFont = QFont("Monospace")
            return myFont
        return None

    def rowCount(self, parent: QModelIndex | QPersistentModelIndex = QModelIndex()) -> int:
        return len(self.dateTagList)

    def columnCount(self, parent: QModelIndex | QPersistentModelIndex = QModelIndex()) -> int:
        return 2

    def replaceListOfTags(self, mediaFile: MediaFile) -> None:
        self.dateTagList = []
        if mediaFile.EXIFTags:  # if the dict has tags
            # Show the date tags for this file
            for tag in mediaFile.EXIFTags:
                if isTagATimeTag(tag):
                    self.dateTagList.append((tag, mediaFile.EXIFTags[tag]))
        self.layoutChanged.emit()


class TagListModel(QAbstractListModel):
    def __init__(self, mediaFileList: list[MediaFile] | None):
        super().__init__()
        self.tags: list[str] = []
        if mediaFileList:
            self.tags = sorted({tag for mf in mediaFileList for tag in mf.EXIFTags.keys()})

    def rowCount(self, parent: QModelIndex | QPersistentModelIndex = QModelIndex()) -> int:
        return len(self.tags)

    def data(
        self, index: QModelIndex | QPersistentModelIndex, role: int = Qt.ItemDataRole.DisplayRole
    ) -> str | QColor | None:
        if role == Qt.ItemDataRole.DisplayRole and index.isValid():
            return self.tags[index.row()]
        elif role == Qt.ItemDataRole.BackgroundRole:
            # Get some background colours to distinguish tags?
            if any(x in self.tags[index.row()].lower() for x in ["model", "make"]):
                # Tags that have "make" or "model" on them
                return QColor(SunnyBeach.darkOrange)
            if any(x in self.tags[index.row()].lower() for x in ["software"]):
                return QColor(SunnyBeach.orange)
            if any(x in self.tags[index.row()].lower() for x in ["comment"]):
                return QColor(SunnyBeach.yellow)
            # else:
            #     return QColor(SunnyBeach.teal)
        return None

    def replaceListOfTags(self, newMediaFileList: list[MediaFile]) -> None:
        self.tags = sorted({tag for mf in newMediaFileList for tag in mf.EXIFTags.keys()})
        self.layoutChanged.emit()


class ValueListModel(QAbstractListModel):
    def __init__(self, mediaFileList: list[MediaFile] | None, tag: str):
        super().__init__()
        self.values: list[str] = []
        if mediaFileList:
            self.values = sorted({mf.EXIFTags.get(tag) for mf in mediaFileList if tag in mf.EXIFTags})  # pyright: ignore[reportArgumentType]

    def rowCount(self, parent: QModelIndex | QPersistentModelIndex = QModelIndex()) -> int:
        return len(self.values)

    def data(self, index: QModelIndex | QPersistentModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> str | None:
        if role == Qt.ItemDataRole.DisplayRole and index.isValid():
            return self.values[index.row()]
        return None

    def replaceListOfValues(self, newMediaFileList: list[MediaFile], newTag: str) -> None:
        self.values = sorted({str(mf.EXIFTags.get(newTag)) for mf in newMediaFileList if newTag in mf.EXIFTags})  # pyright: ignore[reportArgumentType]
        self.layoutChanged.emit()


class FileListModel(QAbstractListModel):
    def __init__(self, mediaFileList: list[MediaFile] | None, tag: str, value: str):
        super().__init__()
        self.files: list[str] = []
        if mediaFileList:
            self.files = [str(mf.fileName) for mf in mediaFileList if mf.EXIFTags.get(tag) == value]

    def rowCount(self, parent: QModelIndex | QPersistentModelIndex = QModelIndex()) -> int:
        return len(self.files)

    def data(self, index: QModelIndex | QPersistentModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> str | None:
        if role == Qt.ItemDataRole.DisplayRole and index.isValid():
            return self.files[index.row()]
        return None

    def replaceListOfFiles(self, newMediaFileList: list[MediaFile], newTag: str, newValue: str) -> None:
        self.files = [str(mf.fileName) for mf in newMediaFileList if mf.EXIFTags.get(newTag) == newValue]
        self.layoutChanged.emit()
