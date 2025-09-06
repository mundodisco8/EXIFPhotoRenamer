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
from PySide6.QtWidgets import (QApplication, QDialog, QGridLayout, QLabel,
    QLayout, QLineEdit, QSizePolicy, QVBoxLayout,
    QWidget)

class Ui_MediaFileViewer(object):
    def setupUi(self, MediaFileViewer):
        if not MediaFileViewer.objectName():
            MediaFileViewer.setObjectName(u"MediaFileViewer")
        MediaFileViewer.resize(511, 660)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MediaFileViewer.sizePolicy().hasHeightForWidth())
        MediaFileViewer.setSizePolicy(sizePolicy)
        MediaFileViewer.setMaximumSize(QSize(16777215, 660))
        MediaFileViewer.setSizeIncrement(QSize(1, 0))
        self.widget = QWidget(MediaFileViewer)
        self.widget.setObjectName(u"widget")
        self.widget.setGeometry(QRect(11, 11, 486, 636))
        self.verticalLayout = QVBoxLayout(self.widget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setSizeConstraint(QLayout.SizeConstraint.SetMinimumSize)
        self.filePathLbl = QLabel(self.widget)
        self.filePathLbl.setObjectName(u"filePathLbl")
        font = QFont()
        font.setBold(True)
        self.filePathLbl.setFont(font)

        self.gridLayout.addWidget(self.filePathLbl, 0, 0, 1, 1)

        self.filePathTxt = QLineEdit(self.widget)
        self.filePathTxt.setObjectName(u"filePathTxt")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(1)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.filePathTxt.sizePolicy().hasHeightForWidth())
        self.filePathTxt.setSizePolicy(sizePolicy1)
        self.filePathTxt.setMinimumSize(QSize(400, 0))
        self.filePathTxt.setSizeIncrement(QSize(1, 0))

        self.gridLayout.addWidget(self.filePathTxt, 0, 1, 1, 1)

        self.dateTimeLbl = QLabel(self.widget)
        self.dateTimeLbl.setObjectName(u"dateTimeLbl")
        self.dateTimeLbl.setFont(font)

        self.gridLayout.addWidget(self.dateTimeLbl, 1, 0, 1, 1)

        self.dateTimeTxt = QLineEdit(self.widget)
        self.dateTimeTxt.setObjectName(u"dateTimeTxt")
        sizePolicy1.setHeightForWidth(self.dateTimeTxt.sizePolicy().hasHeightForWidth())
        self.dateTimeTxt.setSizePolicy(sizePolicy1)
        self.dateTimeTxt.setMinimumSize(QSize(400, 0))
        self.dateTimeTxt.setSizeIncrement(QSize(1, 0))

        self.gridLayout.addWidget(self.dateTimeTxt, 1, 1, 1, 1)

        self.sidecarLbl = QLabel(self.widget)
        self.sidecarLbl.setObjectName(u"sidecarLbl")
        self.sidecarLbl.setFont(font)

        self.gridLayout.addWidget(self.sidecarLbl, 2, 0, 1, 1)

        self.sidecarTxt = QLineEdit(self.widget)
        self.sidecarTxt.setObjectName(u"sidecarTxt")
        sizePolicy1.setHeightForWidth(self.sidecarTxt.sizePolicy().hasHeightForWidth())
        self.sidecarTxt.setSizePolicy(sizePolicy1)
        self.sidecarTxt.setMinimumSize(QSize(400, 0))
        self.sidecarTxt.setSizeIncrement(QSize(1, 0))

        self.gridLayout.addWidget(self.sidecarTxt, 2, 1, 1, 1)

        self.sourceLbl = QLabel(self.widget)
        self.sourceLbl.setObjectName(u"sourceLbl")
        self.sourceLbl.setFont(font)

        self.gridLayout.addWidget(self.sourceLbl, 3, 0, 1, 1)

        self.sourceTxt = QLineEdit(self.widget)
        self.sourceTxt.setObjectName(u"sourceTxt")
        sizePolicy1.setHeightForWidth(self.sourceTxt.sizePolicy().hasHeightForWidth())
        self.sourceTxt.setSizePolicy(sizePolicy1)
        self.sourceTxt.setMinimumSize(QSize(400, 0))
        self.sourceTxt.setSizeIncrement(QSize(1, 0))

        self.gridLayout.addWidget(self.sourceTxt, 3, 1, 1, 1)


        self.verticalLayout.addLayout(self.gridLayout)

        self.imageLbl = QLabel(self.widget)
        self.imageLbl.setObjectName(u"imageLbl")
        self.imageLbl.setMinimumSize(QSize(0, 500))

        self.verticalLayout.addWidget(self.imageLbl)


        self.retranslateUi(MediaFileViewer)

        QMetaObject.connectSlotsByName(MediaFileViewer)
    # setupUi

    def retranslateUi(self, MediaFileViewer):
        MediaFileViewer.setWindowTitle(QCoreApplication.translate("MediaFileViewer", u"MediaFileViewer", None))
        self.filePathLbl.setText(QCoreApplication.translate("MediaFileViewer", u"File Path", None))
        self.dateTimeLbl.setText(QCoreApplication.translate("MediaFileViewer", u"Date/Time", None))
        self.sidecarLbl.setText(QCoreApplication.translate("MediaFileViewer", u"Sidecar?", None))
        self.sidecarTxt.setText("")
        self.sourceLbl.setText(QCoreApplication.translate("MediaFileViewer", u"Source", None))
        self.sourceTxt.setText("")
        self.imageLbl.setText(QCoreApplication.translate("MediaFileViewer", u"TextLabel", None))
    # retranslateUi

