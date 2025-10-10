"""Model Definitions

Still not sure what this model/view thing is but here are some models for you
"""

from enum import StrEnum

from PySide6.QtCore import QAbstractListModel, QAbstractTableModel, QModelIndex, QPersistentModelIndex, Qt
from PySide6.QtGui import QColor, QFont

from MassRenamer.MassRenamerClasses import MediaFile, isTagATimeTag


class SunnyBeach(StrEnum):
    """Sunny Beach Day Palette"""

    blue = "#70a7bd"
    teal = "#7bdcd0"
    yellow = "#f3dfaf"
    orange = "#f9cdaa"
    darkOrange = "#f2b2a2"


class toRenameModel(QAbstractTableModel):
    """A model to show renameable files and their proposed new names together

    Stores a list of tuples (str, str|none) with the format
        (currentFilename, proposedNewName)
    """

    def __init__(self, mediaFileList: list[MediaFile] | None = None) -> None:
        """Creates a list of current filenames and their proposed new names from a list of MediaFile

        Only MediaFiles that have a proposed new name are shown, and only for those that have a different proposed new
        name than their current name.
        The list is internally stored in toRenameList.
        If no list is passed, "returns" an empty list.

        Args:
            mediaFileList (list[MediaFile] | None, optional): A list of MediaFile that can be renamed and their proposed
            new names.
            Defaults to None.
        """
        self.columns = ["Current Filename", "Proposed New Name"]
        super().__init__()

        self.toRenameList: list[tuple[str, str]] = []
        if mediaFileList:
            for instance in mediaFileList:
                if instance.newName and instance.fileName != instance.newName:
                    self.toRenameList.append((str(instance.fileName), str(instance.newName)))

    def data(self, index: QModelIndex | QPersistentModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> str | None:
        """Implementation of the data virtual method.

        Args:
            index (QModelIndex | QPersistentModelIndex): coordinates of the item to return
            role (int, optional): model role. Defaults to Qt.ItemDataRole.DisplayRole.

        Returns:
            str | None: if the selected model is DisplayRole, returns the data in the position (column, row),
            None otherwise
        """
        if role == Qt.ItemDataRole.DisplayRole:
            return self.toRenameList[index.row()][index.column()]
        # TODO: If has sidecar, paint background?
        return None

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.ItemDataRole.DisplayRole):
        """Sets the column's names

        Args:
            section (int): column number
            orientation (Qt.Orientation): the object's orientation, we are only handling Horizontal
            role (int, optional):the model's role. Defaults to Qt.ItemDataRole.DisplayRole.

        Returns:
            str: returns the column's name.
        """
        # for setting columns name
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return f"{self.columns[section]}"

    def rowCount(self, parent: QModelIndex | QPersistentModelIndex | None = None) -> int:
        """Returns the number of data rows

        Args:
            parent (QModelIndex | QPersistentModelIndex, optional): unused argument required by Qt model interface.

        Returns:
            int: returns the number of rows of the model
        """
        if parent is None:
            parent = QModelIndex()
        return len(self.toRenameList)

    def columnCount(self, parent: QModelIndex | QPersistentModelIndex | None = None) -> int:
        """Returns the number of data columns

        Args:
            parent (QModelIndex | QPersistentModelIndex, optional): unused argument required by Qt model interface.

        Returns:
            int: returns the number of colums of the model
        """
        if parent is None:
            parent = QModelIndex()
        return 2

    def replaceListOfFiles(self, mediaFileList: list[MediaFile]) -> None:
        """Update the model's data

        Updates the model's data from a list of MediaFile

        Args:
            mediaFileList (list[MediaFile]): new MediaFile list to use
        """
        self.toRenameList = []
        for instance in mediaFileList:
            if instance.newName and instance.fileName != instance.newName:
                self.toRenameList.append((str(instance.fileName), str(instance.newName)))
        self.layoutChanged.emit()

    def returnColumn(self, column: int) -> list[str]:
        """Returns all the data for a single column as a list of string

        Args:
            column (int): the column to return

        Returns:
            list[str]: a list of str with all the data for a single column
        """
        retList: list[str] = []
        if column > self.columnCount():
            return []
        for item in self.toRenameList:
            retList.append(item[column])
        return retList


class showDatelessModel(QAbstractTableModel):
    """A model for the dateless items table

    Stores a list of items that don't have currently a poposed date, and any proposed new dates for them. It stores it
    in a list of tuple (str, str) with the format
        (fileName, proposedNewDate)

    If no date has been proposed yet, the proposed date column is empty.
    """

    def __init__(self, mediaFileList: list[MediaFile] | None = None) -> None:
        """Inits the class from a list of MediaFile.

        Checks a list of MediaFile and stores the filenames of those that don't have a date yet.

        Args:
            mediaFileList: list[MediaFile] | None, optional): A list of MediaFile
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
        """Implementation of the data virtual method.

        Args:
            index (QModelIndex | QPersistentModelIndex): coordinates of the item to return
            role (int, optional): model role. Defaults to Qt.ItemDataRole.DisplayRole.

        Returns:
            str | None: if the selected model is DisplayRole, returns the data in the position (column, row),
            None otherwise
        """
        if role == Qt.ItemDataRole.DisplayRole:
            return self.datelessItemsList[index.row()][index.column()]
        return None

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.ItemDataRole.DisplayRole):
        """Sets the column's names

        Args:
            section (int): column number
            orientation (Qt.Orientation): the object's orientation, we are only handling Horizontal
            role (int, optional):the model's role. Defaults to Qt.ItemDataRole.DisplayRole.

        Returns:
            str: returns the column's name.
        """
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return f"{self.columns[section]}"

    def rowCount(self, parent: QModelIndex | QPersistentModelIndex | None = None) -> int:
        """Returns the number of data rows

        Args:
            parent (QModelIndex | QPersistentModelIndex, optional): not used. Defaults to QModelIndex().

        Returns:
            int: returns the number of rows of the model
        """
        if parent is None:
            parent = QModelIndex()
        return len(self.datelessItemsList)

    def columnCount(self, parent: QModelIndex | QPersistentModelIndex | None = None) -> int:
        """Returns the number of data columns

        Args:
            parent (QModelIndex | QPersistentModelIndex, optional): not used. Defaults to QModelIndex().

        Returns:
            int: returns the number of colums of the model
        """
        if parent is None:
            parent = QModelIndex()
        return 2

    def replaceListOfFiles(self, mediaFileList: list[MediaFile]) -> None:
        """Update the model's data

        Updates the model's data from a list of MediaFile

        Args:
            mediaFileList (list[MediaFile]): new MediaFile list to use
        """
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
        """Implementation of the data virtual method.

        Shows data but also colorizes the background based on the type of data contained.

        Args:
            index (QModelIndex | QPersistentModelIndex): coordinates of the item to return
            role (int, optional): model role. Defaults to Qt.ItemDataRole.DisplayRole.

        Returns:
            str | None: if the selected model is DisplayRole, returns the data in the position (column, row),
            None otherwise
        """
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

    def rowCount(self, parent: QModelIndex | QPersistentModelIndex | None = None) -> int:
        """Returns the number of data rows

        Args:
            parent (QModelIndex | QPersistentModelIndex, optional): not used. Defaults to QModelIndex().

        Returns:
            int: returns the number of rows of the model
        """
        if parent is None:
            parent = QModelIndex()
        return len(self.dateTagList)

    def columnCount(self, parent: QModelIndex | QPersistentModelIndex | None = None) -> int:
        """Returns the number of data columns

        Args:
            parent (QModelIndex | QPersistentModelIndex, optional): not used. Defaults to QModelIndex().

        Returns:
            int: returns the number of colums of the model
        """
        if parent is None:
            parent = QModelIndex()
        return 2

    def replaceListOfTags(self, mediaFile: MediaFile) -> None:
        """Update the model's data

        Updates the model's data from the dates contained on the selected MediaFile

        Args:
            mediaFile (MediaFile): new MediaFile to use
        """
        self.dateTagList = []
        if mediaFile.EXIFTags:  # if the dict has tags
            # Show the date tags for this file
            for tag in mediaFile.EXIFTags:
                if isTagATimeTag(tag):
                    self.dateTagList.append((tag, mediaFile.EXIFTags[tag]))
        self.layoutChanged.emit()


class TagListModel(QAbstractListModel):
    """A model containint all the EXIF Tag categories on a list of MediaFile"""

    def __init__(self, mediaFileList: list[MediaFile] | None):
        super().__init__()
        self.tags: list[str] = []
        if mediaFileList:
            self.tags = sorted({tag for mf in mediaFileList for tag in mf.EXIFTags})

    def rowCount(self, parent: QModelIndex | QPersistentModelIndex | None = None) -> int:
        """Returns the number of data rows

        Args:
            parent (QModelIndex | QPersistentModelIndex, optional): not used. Defaults to QModelIndex().

        Returns:
            int: returns the number of rows of the model
        """
        if parent is None:
            parent = QModelIndex()
        return len(self.tags)

    def data(
        self, index: QModelIndex | QPersistentModelIndex, role: int = Qt.ItemDataRole.DisplayRole
    ) -> str | QColor | None:
        """Implementation of the data virtual method.

        Shows data but also colorizes the background based on the type of data contained.

        Args:
            index (QModelIndex | QPersistentModelIndex): coordinates of the item to return
            role (int, optional): model role. Defaults to Qt.ItemDataRole.DisplayRole.

        Returns:
            str | None: if the selected model is DisplayRole, returns the data in the position (column, row),
            None otherwise
        """
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
        """Update the model's data

        Updates the model's data from the EXIF Tags contained on the  list of MediaFile

        Args:
            newMediaFileList (list[MediaFile]): new MediaFile to use
        """
        self.tags = sorted({tag for mf in newMediaFileList for tag in mf.EXIFTags})
        self.layoutChanged.emit()


class ValueListModel(QAbstractListModel):
    """A model containint all the values of a particular EXIF Tag on a list of MediaFile"""

    def __init__(self, mediaFileList: list[MediaFile] | None, tag: str):
        super().__init__()
        self.values: list[str] = []
        if mediaFileList:
            self.values = sorted({mf.EXIFTags.get(tag) for mf in mediaFileList if tag in mf.EXIFTags})  # pyright: ignore[reportArgumentType]

    def rowCount(self, parent: QModelIndex | QPersistentModelIndex | None = None) -> int:
        """Returns the number of data rows

        Args:
            parent (QModelIndex | QPersistentModelIndex, optional): not used. Defaults to QModelIndex().

        Returns:
            int: returns the number of rows of the model
        """
        if parent is None:
            parent = QModelIndex()
        return len(self.values)

    def data(self, index: QModelIndex | QPersistentModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> str | None:
        """Implementation of the data virtual method.

        Args:
            index (QModelIndex | QPersistentModelIndex): coordinates of the item to return
            role (int, optional): model role. Defaults to Qt.ItemDataRole.DisplayRole.

        Returns:
            str | None: if the selected model is DisplayRole, returns the data in the position (column, row),
            None otherwise
        """
        if role == Qt.ItemDataRole.DisplayRole and index.isValid():
            return self.values[index.row()]
        return None

    def replaceListOfValues(self, newMediaFileList: list[MediaFile], newTag: str) -> None:
        """Update the model's data

        Args:
            newMediaFileList (list[MediaFile]): list of MediaFile to use
            newTag (str): the tag selected
        """
        self.values = sorted({str(mf.EXIFTags.get(newTag)) for mf in newMediaFileList if newTag in mf.EXIFTags})  # pyright: ignore[reportArgumentType]
        self.layoutChanged.emit()


class FileListModel(QAbstractListModel):
    """A model to show all the files that contain a certain value for a certain ExifTag"""

    def __init__(self, mediaFileList: list[MediaFile] | None, tag: str, value: str):
        super().__init__()
        self.files: list[str] = []
        if mediaFileList:
            self.files = [str(mf.fileName) for mf in mediaFileList if mf.EXIFTags.get(tag) == value]

    def rowCount(self, parent: QModelIndex | QPersistentModelIndex | None = None) -> int:
        """Returns the number of data rows

        Args:
            parent (QModelIndex | QPersistentModelIndex, optional): not used. Defaults to QModelIndex().

        Returns:
            int: returns the number of rows of the model
        """
        if parent is None:
            parent = QModelIndex()
        return len(self.files)

    def data(self, index: QModelIndex | QPersistentModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> str | None:
        """Implementation of the data virtual method.

        Args:
            index (QModelIndex | QPersistentModelIndex): coordinates of the item to return
            role (int, optional): model role. Defaults to Qt.ItemDataRole.DisplayRole.

        Returns:
            str | None: if the selected model is DisplayRole, returns the data in the position (column, row),
            None otherwise
        """
        if role == Qt.ItemDataRole.DisplayRole and index.isValid():
            return self.files[index.row()]
        return None

    def replaceListOfFiles(self, newMediaFileList: list[MediaFile], newTag: str, newValue: str) -> None:
        """Update the model's data

        Updates the model's data from a list of MediaFile, the ExifTag selected and the value for that tag

        Args:
            newMediaFileList (list[MediaFile]): list of mediaFile to get the filenames
            newTag (str): tag to use
            newValue (str): value for said tag
        """
        self.files = [str(mf.fileName) for mf in newMediaFileList if mf.EXIFTags.get(newTag) == newValue]
        self.layoutChanged.emit()
