# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mediaFileViewer.ui'
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
from PySide6.QtWidgets import (QApplication, QDialog, QGridLayout, QHBoxLayout,
    QLabel, QLayout, QLineEdit, QPlainTextEdit,
    QSizePolicy, QTabWidget, QVBoxLayout, QWidget)

class Ui_MediaFileViewer(object):
    def setupUi(self, MediaFileViewer):
        if not MediaFileViewer.objectName():
            MediaFileViewer.setObjectName(u"MediaFileViewer")
        MediaFileViewer.resize(513, 660)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MediaFileViewer.sizePolicy().hasHeightForWidth())
        MediaFileViewer.setSizePolicy(sizePolicy)
        MediaFileViewer.setMaximumSize(QSize(16777215, 660))
        MediaFileViewer.setSizeIncrement(QSize(1, 0))
        self.widget = QWidget(MediaFileViewer)
        self.widget.setObjectName(u"widget")
        self.widget.setGeometry(QRect(10, 12, 486, 667))
        self.verticalLayout = QVBoxLayout(self.widget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setSizeConstraint(QLayout.SizeConstraint.SetMinimumSize)
        self.sidecarLbl = QLabel(self.widget)
        self.sidecarLbl.setObjectName(u"sidecarLbl")
        font = QFont()
        font.setBold(True)
        self.sidecarLbl.setFont(font)

        self.gridLayout.addWidget(self.sidecarLbl, 2, 0, 1, 1)

        self.dateTimeLbl = QLabel(self.widget)
        self.dateTimeLbl.setObjectName(u"dateTimeLbl")
        self.dateTimeLbl.setFont(font)

        self.gridLayout.addWidget(self.dateTimeLbl, 1, 0, 1, 1)

        self.sidecarTxt = QLineEdit(self.widget)
        self.sidecarTxt.setObjectName(u"sidecarTxt")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(1)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.sidecarTxt.sizePolicy().hasHeightForWidth())
        self.sidecarTxt.setSizePolicy(sizePolicy1)
        self.sidecarTxt.setMinimumSize(QSize(400, 0))
        self.sidecarTxt.setSizeIncrement(QSize(1, 0))

        self.gridLayout.addWidget(self.sidecarTxt, 2, 1, 1, 1)

        self.dateTimeTxt = QLineEdit(self.widget)
        self.dateTimeTxt.setObjectName(u"dateTimeTxt")
        sizePolicy1.setHeightForWidth(self.dateTimeTxt.sizePolicy().hasHeightForWidth())
        self.dateTimeTxt.setSizePolicy(sizePolicy1)
        self.dateTimeTxt.setMinimumSize(QSize(400, 0))
        self.dateTimeTxt.setSizeIncrement(QSize(1, 0))

        self.gridLayout.addWidget(self.dateTimeTxt, 1, 1, 1, 1)

        self.sourceLbl = QLabel(self.widget)
        self.sourceLbl.setObjectName(u"sourceLbl")
        self.sourceLbl.setFont(font)

        self.gridLayout.addWidget(self.sourceLbl, 3, 0, 1, 1)

        self.filePathTxt = QLineEdit(self.widget)
        self.filePathTxt.setObjectName(u"filePathTxt")
        sizePolicy1.setHeightForWidth(self.filePathTxt.sizePolicy().hasHeightForWidth())
        self.filePathTxt.setSizePolicy(sizePolicy1)
        self.filePathTxt.setMinimumSize(QSize(400, 0))
        self.filePathTxt.setSizeIncrement(QSize(1, 0))

        self.gridLayout.addWidget(self.filePathTxt, 0, 1, 1, 1)

        self.filePathLbl = QLabel(self.widget)
        self.filePathLbl.setObjectName(u"filePathLbl")
        self.filePathLbl.setFont(font)

        self.gridLayout.addWidget(self.filePathLbl, 0, 0, 1, 1)

        self.sourceTxt = QLineEdit(self.widget)
        self.sourceTxt.setObjectName(u"sourceTxt")
        sizePolicy1.setHeightForWidth(self.sourceTxt.sizePolicy().hasHeightForWidth())
        self.sourceTxt.setSizePolicy(sizePolicy1)
        self.sourceTxt.setMinimumSize(QSize(400, 0))
        self.sourceTxt.setSizeIncrement(QSize(1, 0))

        self.gridLayout.addWidget(self.sourceTxt, 3, 1, 1, 1)


        self.verticalLayout.addLayout(self.gridLayout)

        self.tabWidget = QTabWidget(self.widget)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tab_3 = QWidget()
        self.tab_3.setObjectName(u"tab_3")
        self.horizontalLayout = QHBoxLayout(self.tab_3)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.imageLbl = QLabel(self.tab_3)
        self.imageLbl.setObjectName(u"imageLbl")
        self.imageLbl.setMinimumSize(QSize(0, 0))
        self.imageLbl.setMaximumSize(QSize(450, 450))

        self.horizontalLayout.addWidget(self.imageLbl)

        self.tabWidget.addTab(self.tab_3, "")
        self.tab_4 = QWidget()
        self.tab_4.setObjectName(u"tab_4")
        self.horizontalLayout_2 = QHBoxLayout(self.tab_4)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.tagsTxt = QPlainTextEdit(self.tab_4)
        self.tagsTxt.setObjectName(u"tagsTxt")
        self.tagsTxt.setMaximumSize(QSize(450, 450))

        self.horizontalLayout_2.addWidget(self.tagsTxt)

        self.tabWidget.addTab(self.tab_4, "")

        self.verticalLayout.addWidget(self.tabWidget)


        self.retranslateUi(MediaFileViewer)

        self.tabWidget.setCurrentIndex(1)


        QMetaObject.connectSlotsByName(MediaFileViewer)
    # setupUi

    def retranslateUi(self, MediaFileViewer):
        MediaFileViewer.setWindowTitle(QCoreApplication.translate("MediaFileViewer", u"MediaFileViewer", None))
        self.sidecarLbl.setText(QCoreApplication.translate("MediaFileViewer", u"Sidecar?", None))
        self.dateTimeLbl.setText(QCoreApplication.translate("MediaFileViewer", u"Date/Time", None))
        self.sidecarTxt.setText("")
        self.sourceLbl.setText(QCoreApplication.translate("MediaFileViewer", u"Source", None))
        self.filePathLbl.setText(QCoreApplication.translate("MediaFileViewer", u"File Path", None))
        self.sourceTxt.setText("")
        self.imageLbl.setText(QCoreApplication.translate("MediaFileViewer", u"TextLabel", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_3), QCoreApplication.translate("MediaFileViewer", u"Image Preview", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_4), QCoreApplication.translate("MediaFileViewer", u"Tags", None))
    # retranslateUi

