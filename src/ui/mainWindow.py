# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mainwindow.ui'
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
from PySide6.QtWidgets import (QApplication, QGridLayout, QHBoxLayout, QLabel,
    QLineEdit, QListWidget, QListWidgetItem, QProgressBar,
    QPushButton, QSizePolicy, QSpacerItem, QVBoxLayout,
    QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1600, 1200)
        self.pushButton_2 = QPushButton(MainWindow)
        self.pushButton_2.setObjectName(u"pushButton_2")
        self.pushButton_2.setGeometry(QRect(1420, 1010, 93, 29))
        self.pushButton_3 = QPushButton(MainWindow)
        self.pushButton_3.setObjectName(u"pushButton_3")
        self.pushButton_3.setGeometry(QRect(1420, 1060, 93, 29))
        self.layoutWidget = QWidget(MainWindow)
        self.layoutWidget.setObjectName(u"layoutWidget")
        self.layoutWidget.setGeometry(QRect(62, 152, 1452, 872))
        self.gridLayout = QGridLayout(self.layoutWidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setHorizontalSpacing(50)
        self.gridLayout.setVerticalSpacing(0)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.label_2 = QLabel(self.layoutWidget)
        self.label_2.setObjectName(u"label_2")
        font = QFont()
        font.setBold(True)
        self.label_2.setFont(font)

        self.gridLayout.addWidget(self.label_2, 0, 0, 1, 1)

        self.label_3 = QLabel(self.layoutWidget)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setFont(font)

        self.gridLayout.addWidget(self.label_3, 0, 1, 1, 1)

        self.toRenameList = QListWidget(self.layoutWidget)
        self.toRenameList.setObjectName(u"toRenameList")
        self.toRenameList.setMinimumSize(QSize(700, 800))

        self.gridLayout.addWidget(self.toRenameList, 1, 0, 1, 1)

        self.namePreviewList = QListWidget(self.layoutWidget)
        self.namePreviewList.setObjectName(u"namePreviewList")
        self.namePreviewList.setMinimumSize(QSize(700, 800))

        self.gridLayout.addWidget(self.namePreviewList, 1, 1, 1, 1)

        self.layoutWidget_2 = QWidget(MainWindow)
        self.layoutWidget_2.setObjectName(u"layoutWidget_2")
        self.layoutWidget_2.setGeometry(QRect(60, 90, 598, 31))
        self.JSONhorizontalLayout = QHBoxLayout(self.layoutWidget_2)
        self.JSONhorizontalLayout.setObjectName(u"JSONhorizontalLayout")
        self.JSONhorizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.label_4 = QLabel(self.layoutWidget_2)
        self.label_4.setObjectName(u"label_4")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_4.sizePolicy().hasHeightForWidth())
        self.label_4.setSizePolicy(sizePolicy)
        self.label_4.setFont(font)

        self.JSONhorizontalLayout.addWidget(self.label_4)

        self.currJSONTxt = QLineEdit(self.layoutWidget_2)
        self.currJSONTxt.setObjectName(u"currJSONTxt")
        self.currJSONTxt.setMinimumSize(QSize(300, 0))

        self.JSONhorizontalLayout.addWidget(self.currJSONTxt)

        self.openJSONBtn = QPushButton(self.layoutWidget_2)
        self.openJSONBtn.setObjectName(u"openJSONBtn")

        self.JSONhorizontalLayout.addWidget(self.openJSONBtn)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.JSONhorizontalLayout.addItem(self.horizontalSpacer_2)

        self.layoutWidget_3 = QWidget(MainWindow)
        self.layoutWidget_3.setObjectName(u"layoutWidget_3")
        self.layoutWidget_3.setGeometry(QRect(60, 50, 598, 31))
        self.horizontalLayout = QHBoxLayout(self.layoutWidget_3)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.label = QLabel(self.layoutWidget_3)
        self.label.setObjectName(u"label")
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setFont(font)

        self.horizontalLayout.addWidget(self.label)

        self.currDirTxt = QLineEdit(self.layoutWidget_3)
        self.currDirTxt.setObjectName(u"currDirTxt")
        self.currDirTxt.setMinimumSize(QSize(300, 0))

        self.horizontalLayout.addWidget(self.currDirTxt)

        self.openFolderBtn = QPushButton(self.layoutWidget_3)
        self.openFolderBtn.setObjectName(u"openFolderBtn")

        self.horizontalLayout.addWidget(self.openFolderBtn)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.widget = QWidget(MainWindow)
        self.widget.setObjectName(u"widget")
        self.widget.setGeometry(QRect(80, 1090, 1431, 61))
        self.verticalLayout = QVBoxLayout(self.widget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.progressBarTxt = QLabel(self.widget)
        self.progressBarTxt.setObjectName(u"progressBarTxt")

        self.verticalLayout.addWidget(self.progressBarTxt)

        self.progressBar = QProgressBar(self.widget)
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


        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"EXIF Renamer", None))
        self.pushButton_2.setText(QCoreApplication.translate("MainWindow", u"Rename", None))
        self.pushButton_3.setText(QCoreApplication.translate("MainWindow", u"PushButton", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"Files To Rename", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"Name Preview", None))
        self.label_4.setText(QCoreApplication.translate("MainWindow", u"Load a JSON", None))
        self.openJSONBtn.setText(QCoreApplication.translate("MainWindow", u"&Open Folder", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"Open A Folder", None))
        self.openFolderBtn.setText(QCoreApplication.translate("MainWindow", u"&Open Folder", None))
        self.progressBarTxt.setText("")
    # retranslateUi

