from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QVBoxLayout, QWidget, QCheckBox, QRadioButton

from src.YTDL.logic.ffmpeg import FFMpegThreadToMP3
from src.components.headerwithlinewidget import Header
from src.components.inputwithlabelwidget import InputWithLabel
from src.Config import settings


class FFMpegWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName('FFMpegWidget')
        self.setLayout(QVBoxLayout())
        self.layout().setAlignment(Qt.AlignTop)
        self.layout().setSpacing(0)

        # header
        self.header = Header("Conversion", self)
        self.layout().addWidget(self.header)

        # content
        self.content = QWidget(self)
        self.content.setLayout(QVBoxLayout())
        self.content.layout().setAlignment(Qt.AlignTop)
        self.content.layout().setSpacing(10)
        self.content.layout().setContentsMargins(20, 0, 20, 0)

        self.ext = InputWithLabel("Extension", self)
        self.codec = InputWithLabel("Codec", self)
        self.quick_convert = InputWithLabel("Quick Convert", self)
        button = QRadioButton(self)
        button.setFixedWidth(15)
        button.setFixedHeight(15)
        button.clicked.connect(self.toggle_quick_convert)
        self.quick_convert.set_input(button)

        self.content.layout().addWidget(self.ext)
        self.content.layout().addWidget(self.quick_convert)
        self.content.layout().addWidget(self.codec)

        self.layout().addWidget(self.content)

        self.load_config()

    def toggle_quick_convert(self):
        if self.quick_convert.input.isChecked():
            self.codec.setDisabled(True)
        else:
            self.codec.setDisabled(False)

    def get_processor(self):
        format = self.ext.get_input()
        if self.quick_convert.input.isChecked():
            return FFMpegThreadToMP3(format=format, fast=True)
        codec = self.codec.get_input()
        return FFMpegThreadToMP3(format=format, codec=codec)

    def load_config(self):
        try:
            self.ext.input.setText(settings.ytdl.extension.get())
            self.codec.input.setText(settings.ytdl.codec.get())
            self.quick_convert.input.setChecked(settings.ytdl.quick_convert.get() == "true")
        except KeyError:
            pass

    def save_config(self):
        settings.ytdl.extension.set(self.ext.get_input())
        settings.ytdl.codec.set(self.codec.get_input())
        settings.ytdl.quick_convert.set(self.quick_convert.input.isChecked())
