# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'renameWarningDialog.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QDialog, QDialogButtonBox,
    QHBoxLayout, QLabel, QPlainTextEdit, QSizePolicy,
    QVBoxLayout, QWidget)

class Ui_renameWarningDialog(object):
    def setupUi(self, renameWarningDialog):
        if not renameWarningDialog.objectName():
            renameWarningDialog.setObjectName(u"renameWarningDialog")
        renameWarningDialog.setWindowModality(Qt.WindowModality.WindowModal)
        renameWarningDialog.resize(480, 640)
        renameWarningDialog.setModal(True)
        self.verticalLayout_2 = QVBoxLayout(renameWarningDialog)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.iconTxt = QLabel(renameWarningDialog)
        self.iconTxt.setObjectName(u"iconTxt")
        font = QFont()
        font.setPointSize(42)
        self.iconTxt.setFont(font)
        self.iconTxt.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.iconTxt.setIndent(0)

        self.horizontalLayout.addWidget(self.iconTxt)

        self.messageTxt = QLabel(renameWarningDialog)
        self.messageTxt.setObjectName(u"messageTxt")

        self.horizontalLayout.addWidget(self.messageTxt)

        self.horizontalLayout.setStretch(0, 10)
        self.horizontalLayout.setStretch(1, 90)

        self.verticalLayout.addLayout(self.horizontalLayout)

        self.fileListTxt = QLabel(renameWarningDialog)
        self.fileListTxt.setObjectName(u"fileListTxt")

        self.verticalLayout.addWidget(self.fileListTxt)

        self.fileListTextEdit = QPlainTextEdit(renameWarningDialog)
        self.fileListTextEdit.setObjectName(u"fileListTextEdit")
        self.fileListTextEdit.setUndoRedoEnabled(False)
        self.fileListTextEdit.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self.fileListTextEdit.setReadOnly(True)

        self.verticalLayout.addWidget(self.fileListTextEdit)


        self.verticalLayout_2.addLayout(self.verticalLayout)

        self.buttonBox = QDialogButtonBox(renameWarningDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Ok)
        self.buttonBox.setCenterButtons(True)

        self.verticalLayout_2.addWidget(self.buttonBox)


        self.retranslateUi(renameWarningDialog)
        self.buttonBox.accepted.connect(renameWarningDialog.accept)
        self.buttonBox.rejected.connect(renameWarningDialog.reject)

        QMetaObject.connectSlotsByName(renameWarningDialog)
    # setupUi

    def retranslateUi(self, renameWarningDialog):
        renameWarningDialog.setWindowTitle(QCoreApplication.translate("renameWarningDialog", u"Dialog", None))
        self.iconTxt.setText(QCoreApplication.translate("renameWarningDialog", u"\u26a0\ufe0f", None))
        self.messageTxt.setText(QCoreApplication.translate("renameWarningDialog", u"TextLabel", None))
        self.fileListTxt.setText(QCoreApplication.translate("renameWarningDialog", u"TextLabel", None))
    # retranslateUi

