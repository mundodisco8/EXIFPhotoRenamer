"""This module provides the RP Renamer main window."""

from pathlib import Path

from PySide6.QtWidgets import QWidget, QFileDialog, QDialog, QListWidgetItem, QHeaderView
from PySide6.QtCore import Slot, QProcess, Qt
from PySide6.QtGui import QPixmap

from ui.mainWindow import Ui_MainWindow
from ui.mediaFileViewer import Ui_MediaFileViewer
from massRenamer.massRenamerClasses import (
    generateSortedMediaFileList,
    getFilesInFolder,
    inferDateFromNeighbours,
    loadExifToolTagsFromFile,
    tagsToExtract,
    MediaFile,
)
from models import fixDateModel, isTagATimeTag, showDatelessModel


class Window(QWidget, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self._setupUI()

        ### Data Structures
        # When we are fixing dates, this list will hold the date that we select for each file. A dict where
        # the key is the name of the file and the value is the currently selected new date for that file
        self.selectedDates: dict[str, str] = {}

        ### UI stuff
        # Open file/folder
        self.openFolderBtn.clicked.connect(self.loadFolder)
        self.openJSONBtn.clicked.connect(self.loadExifTagsFromJSON)
        # Rename files Tab
        self.mediaFileViewerBtn.clicked.connect(self.showMediaFileViewer)
        self.toRenameList.itemClicked.connect(self.updateMediaFileViewer)
        self.mediaFileViewer = MediaFileViewer(self)
        self.refreshFilesToRenameBtn.clicked.connect(self.loadJSON)
        # Fix Dates Tab
        # toFixDates Table: shows the filenames of the files that don't have dates, and the currently selected date for
        # that file, if one has already been chosen
        self.showDatelessModel = showDatelessModel()
        self.toFixDatesTableView.setModel(self.showDatelessModel)
        self.toFixDatesTableView.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.toFixDatesTableView.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.toFixDatesTableView.clicked.connect(self.updateListOfDates)
        # Create a model for the date fixer view, and assign it to the View widget
        self.fixDateModel = fixDateModel()
        self.datesTableView.setModel(self.fixDateModel)
        self.datesTableView.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.datesTableView.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.datesTableView.clicked.connect(self.dateSelected)
        self.setDateBtn.clicked.connect(self.assignNewDates)

    def _setupUI(self):
        self.setupUi(self)  # pyright: ignore[reportUnknownMemberType]

    @Slot()
    def processStarts(self) -> None:
        """_summary_"""
        self.toRenameList.addItem("Process Starts")

    @Slot()
    def processEnds(self) -> None:
        """_summary_"""
        self.toRenameList.addItem("Process Ends")

    @Slot()
    def updateProgressBar(self) -> None:
        """_summary_"""
        currVal = self.progressBar.value()
        self.progressBar.setValue(currVal + 1)

    @Slot()
    def loadFolder(self) -> None:
        """Action for the openFolderBtn clicked signal

        Opens a file dialog to allow picking a folder with files to rename. It will grab tags for all procesable files
        recursively and save the tags in a JSON file (as this process can take time for big folders).
        """

        # Let's select a folder and process its files

        self.toRenameList.clear()  # clear the files to rename list on button click
        self.currJSONTxt.clear()  # clear the any current JSON
        # If the currDirTxt lineEdit has text on it, use it as reference for the file dialog. Otherwise, use home() as
        # starting point
        if self.currDirTxt.text():
            initDir = self.currDirTxt.text()
        else:
            # initDir = str(Path.home())  # default to the user's home
            initDir = r"C:\Users\mundo\OneDrive\Desktop\EXIFPhotoRenamer\FotosTest\A"

        self._selDir = QFileDialog.getExistingDirectory(self, "Choose Folder Containing the Files To Rename", initDir)

        # Get the number of files in the dir
        self.progressBarTxt.setText("Countnig processsable files in the folder...")
        self.repaint()  # need this to force the change in UI before we hit the UI in the event loop
        numFiles = getFilesInFolder(Path(self._selDir))
        self.progressBar.setFormat("Processed %v / %m...")
        self.progressBar.setRange(0, numFiles)
        self.progressBar.setValue(0)

        # Tags to Extract
        # The date formatting is super useful, as it's really smart grabbing offsets, I think
        # -a allow duplicate tags
        # -s short tag names (no effect with json output but I'll leave it)
        # -j output json
        # -r recursive folder search
        # -d "%Y-%m-%dT%H:%M:%S%:z" output dates in YYYY-MM-DDTHH:MM:SS+/-Offset
        cmdArgs: list[str] = tagsToExtract + ["-G1", "-a", "-s", "-j", "-r", "-d", "%Y-%m-%dT%H:%M:%S%:z", self._selDir]

        self.p = QProcess()
        self.processOutput: str = ""
        self.p.readyReadStandardOutput.connect(self.handleStdOut)
        self.p.readyReadStandardError.connect(self.handleStdOut)
        self.p.stateChanged.connect(self.handleState)
        self.progressBarTxt.setText("Extracting Tags from Files...")
        self.repaint()
        self.p.start("exiftool", cmdArgs)
        # From here, we listen to the output and handle it in `handleStdOut()` and check the process state and handle it
        # in `handleState()`

    @Slot()
    def handleStdOut(self) -> None:
        """Check the standard out for signs of files being processed and update the progress bar"""
        data = self.p.readAllStandardOutput().toStdString()
        for line in data.splitlines():
            if line:
                line.rstrip()
                self.processOutput += line
                if "SourceFile" in line:
                    self.progressBar.setValue(self.progressBar.value() + 1)
                    self.repaint()

    @Slot()
    def handleState(self, state: QProcess.ProcessState) -> None:
        if state == QProcess.ProcessState.NotRunning:
            saveFile, _ = QFileDialog.getSaveFileName(
                self,
                "Select A File to Save the Tags",
                self._selDir + "/fileTags.json",  # add fileTags.json to suggest it as predetermined file name
                "JSON Files (*.json)",
            )

            # If the Dialog is cancelled, the file returned is ""
            if saveFile:
                with open(Path(saveFile), "w+") as writeFile:
                    writeFile.write(self.processOutput)
                self.progressBarTxt.setText(f"Tags Saved in {saveFile}")
            else:
                self.progressBarTxt.setText("We didn't save the tags :(")

    @Slot()
    def loadJSON(self) -> None:
        """Creates a sorted list of MediaFile instances from a list of dictionaries containing EXIFTool Tags

        It also checks for elements without a date and adds them to the Fix Dates Tab.
        """
        tagsDictList = loadExifToolTagsFromFile(Path(self._jsonFile))

        self.mediaFileList = generateSortedMediaFileList(tagsDictList)

        self.toRenameList.clear()
        datelessFiles: list[tuple[str, str]] = []
        for item in self.mediaFileList:
            if item.dateTime is not None:
                # if the item has a date, send it to the "toRename" list
                self.toRenameList.addItem(str(item.fileName))
                # TEST: For now, we also add dated items to the dateless list, for testing
                datelessFiles.append((str(item.fileName), ""))
            else:
                # if it doesn't, send it to the dateless files list
                # Add an item to the dict with the name of the file as key, and an "empty" date for now
                datelessFiles.append((str(item.fileName), ""))

        # Find Dateless, try to correct them by hand. Get the actual instance that doesn't have a date and its index in
        # the list of MediaFile, as it will be handy later
        dateless: list[tuple[int, MediaFile]] = [
            (index, instance) for index, instance in enumerate(self.mediaFileList) if instance.dateTime is None
        ]

        if len(dateless) > 0:
            for datelessItem in dateless:
                inferredDates = inferDateFromNeighbours(datelessItem[0], self.mediaFileList)
                if inferredDates[0]:
                    self.mediaFileList[datelessItem[0]].EXIFTags["Inferred:LeftDate"] = inferredDates[0]
                if inferredDates[1]:
                    self.mediaFileList[datelessItem[0]].EXIFTags["Inferred:RightDate"] = inferredDates[1]

        self.showDatelessModel.replaceListOfFiles(datelessFiles)

    @Slot()
    def loadExifTagsFromJSON(self) -> None:
        """Selects a JSON file with the output of EXIFTool, and creates a sorted list of MediaFileInstances, pointing
        to files that might need their date fixed.

        Action for the selection of a JSON file dialog.
        """

        # Because we are "starting the process", clean the state
        self.toRenameList.clear()
        self.namePreviewList.clear()
        # FIXME: self.toFixDatesTableView.clear()
        self.selectedDates = {}

        # If the current directory field has something on it, use it as starting point for looking for a JSON
        if self.currDirTxt.text():
            initDir = self.currDirTxt.text()
        else:
            # initDir = str(Path.home())  # default to the user's home
            initDir = r"C:\Users\mundo\OneDrive\Desktop\EXIFPhotoRenamer\FotosTest\A"
        self._jsonFile, _ = QFileDialog.getOpenFileName(self, "Pick a JSON file with your EXIF tags", initDir, "*.json")
        self.currJSONTxt.setText(self._jsonFile)
        # Clear it after the JSON was selected, to avoid ambiguity about what is open
        self.currDirTxt.clear()
        # Create a list of MediaFile instances
        self.loadJSON()

    @Slot()
    def showMediaFileViewer(self) -> None:
        """Shows the MediaFile Viewer"""
        self.mediaFileViewer.show()
        # Reposition Window to the right of the main window on show.
        # X coord is MainWindow's x + MainWindow's width (so both windows match side to side)
        # Y coord is MainWindow's y (so titlebars are aligned in height)
        self.mediaFileViewer.move(self.geometry().x() + self.width(), self.y())

    def _updateMediaFileViewerFromInstance(self, mediaFile: MediaFile) -> None:
        self.mediaFileViewer.filePathTxt.setText(str(mediaFile.fileName))
        self.mediaFileViewer.dateTimeTxt.setText(mediaFile.dateTime)
        self.mediaFileViewer.sidecarTxt.setText(str(mediaFile.sidecar))
        self.mediaFileViewer.sourceTxt.setText(mediaFile.source)
        pixMap = QPixmap(mediaFile.fileName).scaled(
            self.mediaFileViewer.imageLbl.size(), Qt.AspectRatioMode.KeepAspectRatio
        )
        self.mediaFileViewer.imageLbl.setPixmap(pixMap)

    @Slot(QListWidgetItem)
    def updateMediaFileViewer(self, current: QListWidgetItem) -> None:
        # Find an instance of MediaFile that as its filename the text in the currently selected cell of the toRename
        # list
        instance: MediaFile | None = next(
            filter(lambda instance: instance.fileName == Path(current.text()), self.mediaFileList), None
        )

        if instance:
            self._updateMediaFileViewerFromInstance(instance)

    @Slot()
    def updateListOfDates(self) -> None:
        """When we select an item from the Files without a clear date, update the MediaFile viewer pane to get some
        context and then show its date tags so one can be selected
        """

        # To get the selected filename, get the index of the currently selected cell ...
        index = self.toFixDatesTableView.selectionModel().currentIndex()
        # and grab whatever is in column 0
        currFileName = str(index.sibling(index.row(), 0).data())

        # Find an instance of MediaFile that has currFileName as its filename
        instance: MediaFile | None = next(
            filter(lambda instance: instance.fileName == Path(currFileName), self.mediaFileList), None
        )
        if instance:
            # If the selected item is in the list (it should!) then update the mediaViewer pane
            self._updateMediaFileViewerFromInstance(instance)
            if instance.EXIFTags:  # if the dict has tags
                # Show the date tags for this file
                newList: list[tuple[str, str]] = []
                for tag in instance.EXIFTags:
                    if isTagATimeTag(tag):
                        newList.append((tag, instance.EXIFTags[tag]))
                self.fixDateModel.replaceListOfTags(newList)
                # Clear the selection as it might be out of bounds in the new list
                self.datesTableView.clearSelection()
            # And finally, if a date has been selected already, show it
            if str(instance.fileName) in self.selectedDates.keys():
                self.dateChosenTxt.setText(self.selectedDates[str(instance.fileName)])

    @Slot()
    def dateSelected(self) -> None:
        """Action to perform when a date of the available dates to fix a dateless item has been  selected"""

        index = self.datesTableView.selectionModel().currentIndex()
        # Get the value of the time column, no matter which one of the two cells was clicked
        valueStr = str(index.sibling(index.row(), 1).data())
        self.dateChosenTxt.setText(valueStr)
        # If the key doesn't exist, it will add it, and if it does, it will update it
        # To get the selected filename, get the index of the currently selected cell in the toFixDatesTableView
        index = self.toFixDatesTableView.selectionModel().currentIndex()
        # and grab whatever is in column 0
        currFileName = str(index.sibling(index.row(), 0).data())
        self.selectedDates[currFileName] = valueStr

        # Update the Model of the dateless files to show the selected date together with its corresponding filename
        # We can get the index of the list from row of the index of the currently selected cell
        row = self.toFixDatesTableView.selectionModel().currentIndex().row()
        self.showDatelessModel.datelessItemsList[row] = (currFileName, valueStr)
        self.showDatelessModel.layoutChanged.emit()

    @Slot()
    def assignNewDates(self) -> None:
        """Assigns the currently selected dates on their dateless items"""
        # We have a dict with filenames and new dates
        # For item in dict
        #   exiftool put tags in file
        # Remove all the items from the list of dateless

        # To "save" the changes
        #   For item in dict
        #       Patch the mediaFile item
        #       Set date
        # add tags to EXIFTags

        # for item in listofMediaFile
        #   take its EXIFTool member and put it on a string
        # save the JSON

        # Probably reload the new JSON

        pass


class MediaFileViewer(QDialog, Ui_MediaFileViewer):
    def __init__(self, parent: None | QWidget = None):
        super().__init__(parent)
        self._setupUI()

    def _setupUI(self):
        self.setupUi(self)  # pyright: ignore[reportUnknownMemberType]
