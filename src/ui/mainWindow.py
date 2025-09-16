# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mainWindow.ui'
##
## Created by: Qt User Interface Compiler version 6.9.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QCheckBox, QGridLayout, QHBoxLayout,
    QHeaderView, QLabel, QLineEdit, QListView,
    QProgressBar, QPushButton, QSizePolicy, QSpacerItem,
    QTabWidget, QTableView, QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1600, 1200)
        self.progLayoutWidget = QWidget(MainWindow)
        self.progLayoutWidget.setObjectName(u"progLayoutWidget")
        self.progLayoutWidget.setGeometry(QRect(80, 1090, 1431, 61))
        self.verticalLayout = QVBoxLayout(self.progLayoutWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.progressBarTxt = QLabel(self.progLayoutWidget)
        self.progressBarTxt.setObjectName(u"progressBarTxt")

        self.verticalLayout.addWidget(self.progressBarTxt)

        self.progressBar = QProgressBar(self.progLayoutWidget)
        self.progressBar.setObjectName(u"progressBar")
        self.progressBar.setStyleSheet(u"QProgressBar {\n"
"    border: 2px solid grey;\n"
"    border-radius: 5px;\n"
"}\n"
"\n"
"QProgressBar::chunk {\n"
"    background-color: #05B8CC;\n"
"    width: 20px;\n"
"}\n"
"\n"
"QProgressBar {\n"
"    border: 2px solid grey;\n"
"    border-radius: 5px;\n"
"    text-align: center;\n"
"}")
        self.progressBar.setValue(0)

        self.verticalLayout.addWidget(self.progressBar)

        self.tabWidget = QTabWidget(MainWindow)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tabWidget.setGeometry(QRect(50, 140, 1480, 873))
        self.Rename = QWidget()
        self.Rename.setObjectName(u"Rename")
        self.verticalLayout_2 = QVBoxLayout(self.Rename)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")

        self.verticalLayout_2.addLayout(self.horizontalLayout_2)

        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setHorizontalSpacing(50)
        self.gridLayout.setVerticalSpacing(0)
        self.namePreviewList = QListView(self.Rename)
        self.namePreviewList.setObjectName(u"namePreviewList")

        self.gridLayout.addWidget(self.namePreviewList, 2, 1, 1, 1)

        self.label_3 = QLabel(self.Rename)
        self.label_3.setObjectName(u"label_3")
        font = QFont()
        font.setBold(True)
        self.label_3.setFont(font)

        self.gridLayout.addWidget(self.label_3, 0, 1, 1, 1)

        self.toRenameList = QListView(self.Rename)
        self.toRenameList.setObjectName(u"toRenameList")

        self.gridLayout.addWidget(self.toRenameList, 2, 0, 1, 1)

        self.label_2 = QLabel(self.Rename)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setFont(font)

        self.gridLayout.addWidget(self.label_2, 0, 0, 1, 1)

        self.refreshFilesToRenameBtn = QPushButton(self.Rename)
        self.refreshFilesToRenameBtn.setObjectName(u"refreshFilesToRenameBtn")
        self.refreshFilesToRenameBtn.setMinimumSize(QSize(130, 0))

        self.gridLayout.addWidget(self.refreshFilesToRenameBtn, 1, 0, 1, 1)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.renameBtn = QPushButton(self.Rename)
        self.renameBtn.setObjectName(u"renameBtn")

        self.horizontalLayout_5.addWidget(self.renameBtn)

        self.dryRunChkBox = QCheckBox(self.Rename)
        self.dryRunChkBox.setObjectName(u"dryRunChkBox")

        self.horizontalLayout_5.addWidget(self.dryRunChkBox)

        self.horizontalLayout_5.setStretch(0, 80)
        self.horizontalLayout_5.setStretch(1, 20)

        self.gridLayout.addLayout(self.horizontalLayout_5, 3, 1, 1, 1)


        self.verticalLayout_2.addLayout(self.gridLayout)

        self.tabWidget.addTab(self.Rename, "")
        self.Fix_Dates = QWidget()
        self.Fix_Dates.setObjectName(u"Fix_Dates")
        self.dateLayoutWidget = QWidget(self.Fix_Dates)
        self.dateLayoutWidget.setObjectName(u"dateLayoutWidget")
        self.dateLayoutWidget.setGeometry(QRect(11, 11, 1411, 829))
        self.gridLayout_2 = QGridLayout(self.dateLayoutWidget)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.setDateBtn = QPushButton(self.dateLayoutWidget)
        self.setDateBtn.setObjectName(u"setDateBtn")

        self.gridLayout_2.addWidget(self.setDateBtn, 2, 0, 1, 1)

        self.label_5 = QLabel(self.dateLayoutWidget)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setFont(font)

        self.gridLayout_2.addWidget(self.label_5, 0, 0, 1, 1)

        self.datesTableView = QTableView(self.dateLayoutWidget)
        self.datesTableView.setObjectName(u"datesTableView")
        self.datesTableView.setMinimumSize(QSize(400, 0))
        self.datesTableView.setMaximumSize(QSize(16777215, 16777215))
        self.datesTableView.horizontalHeader().setVisible(True)

        self.gridLayout_2.addWidget(self.datesTableView, 1, 2, 1, 1)

        self.toFixDatesTableView = QTableView(self.dateLayoutWidget)
        self.toFixDatesTableView.setObjectName(u"toFixDatesTableView")

        self.gridLayout_2.addWidget(self.toFixDatesTableView, 1, 0, 1, 1)

        self.label_6 = QLabel(self.dateLayoutWidget)
        self.label_6.setObjectName(u"label_6")
        self.label_6.setFont(font)

        self.gridLayout_2.addWidget(self.label_6, 0, 2, 1, 1)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.label_10 = QLabel(self.dateLayoutWidget)
        self.label_10.setObjectName(u"label_10")

        self.horizontalLayout_4.addWidget(self.label_10)

        self.dateChosenTxt = QLineEdit(self.dateLayoutWidget)
        self.dateChosenTxt.setObjectName(u"dateChosenTxt")

        self.horizontalLayout_4.addWidget(self.dateChosenTxt)


        self.gridLayout_2.addLayout(self.horizontalLayout_4, 2, 2, 1, 1)

        self.gridLayout_2.setColumnStretch(0, 7)
        self.tabWidget.addTab(self.Fix_Dates, "")
        self.tab = QWidget()
        self.tab.setObjectName(u"tab")
        self.verticalLayout_7 = QVBoxLayout(self.tab)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.verticalLayout_4 = QVBoxLayout()
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.label_7 = QLabel(self.tab)
        self.label_7.setObjectName(u"label_7")

        self.verticalLayout_4.addWidget(self.label_7)

        self.tagView = QListView(self.tab)
        self.tagView.setObjectName(u"tagView")

        self.verticalLayout_4.addWidget(self.tagView)


        self.horizontalLayout_3.addLayout(self.verticalLayout_4)

        self.verticalLayout_5 = QVBoxLayout()
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.label_8 = QLabel(self.tab)
        self.label_8.setObjectName(u"label_8")

        self.verticalLayout_5.addWidget(self.label_8)

        self.valueView = QListView(self.tab)
        self.valueView.setObjectName(u"valueView")

        self.verticalLayout_5.addWidget(self.valueView)


        self.horizontalLayout_3.addLayout(self.verticalLayout_5)

        self.verticalLayout_6 = QVBoxLayout()
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.label_9 = QLabel(self.tab)
        self.label_9.setObjectName(u"label_9")

        self.verticalLayout_6.addWidget(self.label_9)

        self.fileView = QListView(self.tab)
        self.fileView.setObjectName(u"fileView")

        self.verticalLayout_6.addWidget(self.fileView)


        self.horizontalLayout_3.addLayout(self.verticalLayout_6)


        self.verticalLayout_7.addLayout(self.horizontalLayout_3)

        self.tabWidget.addTab(self.tab, "")
        self.mediaFileViewerBtn = QPushButton(MainWindow)
        self.mediaFileViewerBtn.setObjectName(u"mediaFileViewerBtn")
        self.mediaFileViewerBtn.setGeometry(QRect(1400, 120, 130, 29))
        self.mediaFileViewerBtn.setMinimumSize(QSize(130, 0))
        self.layoutWidget = QWidget(MainWindow)
        self.layoutWidget.setObjectName(u"layoutWidget")
        self.layoutWidget.setGeometry(QRect(60, 50, 558, 71))
        self.verticalLayout_3 = QVBoxLayout(self.layoutWidget)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label = QLabel(self.layoutWidget)
        self.label.setObjectName(u"label")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setFont(font)

        self.horizontalLayout.addWidget(self.label)

        self.currDirTxt = QLineEdit(self.layoutWidget)
        self.currDirTxt.setObjectName(u"currDirTxt")
        self.currDirTxt.setMinimumSize(QSize(300, 0))

        self.horizontalLayout.addWidget(self.currDirTxt)

        self.openFolderBtn = QPushButton(self.layoutWidget)
        self.openFolderBtn.setObjectName(u"openFolderBtn")

        self.horizontalLayout.addWidget(self.openFolderBtn)


        self.verticalLayout_3.addLayout(self.horizontalLayout)

        self.JSONhorizontalLayout = QHBoxLayout()
        self.JSONhorizontalLayout.setObjectName(u"JSONhorizontalLayout")
        self.horizontalSpacer_4 = QSpacerItem(4, 20, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)

        self.JSONhorizontalLayout.addItem(self.horizontalSpacer_4)

        self.label_4 = QLabel(self.layoutWidget)
        self.label_4.setObjectName(u"label_4")
        sizePolicy.setHeightForWidth(self.label_4.sizePolicy().hasHeightForWidth())
        self.label_4.setSizePolicy(sizePolicy)
        self.label_4.setFont(font)

        self.JSONhorizontalLayout.addWidget(self.label_4)

        self.currJSONTxt = QLineEdit(self.layoutWidget)
        self.currJSONTxt.setObjectName(u"currJSONTxt")
        self.currJSONTxt.setMinimumSize(QSize(300, 0))

        self.JSONhorizontalLayout.addWidget(self.currJSONTxt)

        self.openJSONBtn = QPushButton(self.layoutWidget)
        self.openJSONBtn.setObjectName(u"openJSONBtn")

        self.JSONhorizontalLayout.addWidget(self.openJSONBtn)


        self.verticalLayout_3.addLayout(self.JSONhorizontalLayout)


        self.retranslateUi(MainWindow)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"EXIF Renamer", None))
        self.progressBarTxt.setText("")
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"Name Preview", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"Files To Rename", None))
        self.refreshFilesToRenameBtn.setText(QCoreApplication.translate("MainWindow", u"Refresh Files To Rename", None))
        self.renameBtn.setText(QCoreApplication.translate("MainWindow", u"Rename", None))
        self.dryRunChkBox.setText(QCoreApplication.translate("MainWindow", u"Dry Run", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.Rename), QCoreApplication.translate("MainWindow", u"Rename Files", None))
        self.setDateBtn.setText(QCoreApplication.translate("MainWindow", u"Update Dates On Files", None))
        self.label_5.setText(QCoreApplication.translate("MainWindow", u"Files Without a Clear Date", None))
        self.label_6.setText(QCoreApplication.translate("MainWindow", u"Date Tags in File", None))
        self.label_10.setText(QCoreApplication.translate("MainWindow", u"Date Chosen", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.Fix_Dates), QCoreApplication.translate("MainWindow", u"Fix Dates", None))
        self.label_7.setText(QCoreApplication.translate("MainWindow", u"Tags", None))
        self.label_8.setText(QCoreApplication.translate("MainWindow", u"Tag Values", None))
        self.label_9.setText(QCoreApplication.translate("MainWindow", u"File Names", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), QCoreApplication.translate("MainWindow", u"Tag Explorer", None))
        self.mediaFileViewerBtn.setText(QCoreApplication.translate("MainWindow", u"MediaFile Viewer", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"Open A Folder", None))
        self.openFolderBtn.setText(QCoreApplication.translate("MainWindow", u"&Open Folder", None))
        self.label_4.setText(QCoreApplication.translate("MainWindow", u"Load a JSON", None))
        self.openJSONBtn.setText(QCoreApplication.translate("MainWindow", u"&Open Folder", None))
    # retranslateUi

