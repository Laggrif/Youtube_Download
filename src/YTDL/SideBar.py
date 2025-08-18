from os.path import join

from PySide6.QtCore import Qt, QEvent
from PySide6.QtGui import QResizeEvent
from PySide6.QtWidgets import QWidget, QVBoxLayout

from src.Directory import application_path
from src.StyleSheetParser import get_style
from src.YTDL.Ffmpeg import FFMpegWidget
from src.YTDL.Metadata import MetadataWidget
from src.YTDL.Settings import SettingsWidget
from src.components.modifiablelistwidget import ModifiableList
from src.components.scrollbar import ScrollBar
from src.Config import settings


class SideBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        if hasattr(parent, 'config_category'):
            self.config_category = parent.config_category.copy()
        else:
            self.config_category = ['SideBar']
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setObjectName('SideBar')
        self.setStyleSheet(get_style())

        self.content = QWidget(self)
        self.content.setFixedWidth(self.width())
        layout = QVBoxLayout(self.content)
        self.content.setObjectName('SideBarContent')
        self.content.setLayout(layout)

        self.scrollBar = ScrollBar(self)
        self.scrollBar.color = (120, 120, 120)
        self.scrollBar.setObjectName('ScrollBar')
        self.scrollBar.setGeometry(self.width() - 5, 0, 5, int(self.height()**2 / self.content.height()))
        self.scrollBar.view = self.content

        # filters
        self.settings = SettingsWidget(self)

        self.metadata = MetadataWidget(self)

        self.ffmpeg = FFMpegWidget(self)

        # add each element to the layout
        self.content.layout().addWidget(self.settings)
        self.content.layout().addWidget(self.metadata)
        self.content.layout().addWidget(self.ffmpeg)

        # space the elements of the layout
        layout.setSpacing(10)
        self.content.adjustSize()

        self.show()

    def save_config(self):
        if settings.save_on_exit.get():
            self.metadata.save_config()
            self.ffmpeg.save_config()
            self.settings.save_config()
        else:
            self.settings.restore_config()

    def wheelEvent(self, event):
        new_y = self.content.pos().y() + event.angleDelta().y()

        if new_y > 0:
            self.content.move(0, 0)
            self.scrollBar.move(self.scrollBar.x(), 0)
        elif new_y < self.height() - self.content.height():
            self.content.move(0, self.height() - self.content.height())
            self.scrollBar.move(self.scrollBar.x(), self.height() - self.scrollBar.height())
        else:
            self.content.move(0, new_y)
            self.scrollBar.move(self.scrollBar.x(), - int(self.height() * self.content.pos().y() / self.content.height()))

        event.accept()
        self.show()

    def resizeEvent(self, event: QResizeEvent):
        event.accept()
        self.scrollBar.setFixedHeight(int(self.height()**2 / self.content.height()))
        self.scrollBar.move(self.width() - self.scrollBar.width(), self.scrollBar.pos().y())
        self.setGeometry(self.pos().x(), self.pos().y(), event.size().width(), event.size().height())

        self.content.setFixedWidth(self.width())
        self.show()

    def show(self):
        super().show()
        self.content.show()
        self.scrollBar.show()
