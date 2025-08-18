from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout

from src.Config import settings
from src.StyleSheetParser import get_style
from src.components.headerwithlinewidget import Header
from src.components.inputwithlabelwidget import InputWithLabel
from src.components.suggestionwidget import QSuggestionWidget
from src.YTDL.logic.metadata import IMPORTANT_METADATA, AVAILABLE_INFO, MetadataPostProcessor


class MetadataWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        if hasattr(parent, 'config_category'):
            self.config_category = parent.config_category.copy()
            self.config_category.append('Metadata')
        else:
            self.config_category = 'Metadata'
        self.setObjectName('MetadataWidget')
        self.setLayout(QVBoxLayout())
        self.layout().setAlignment(Qt.AlignTop)
        self.layout().setSpacing(0)

        # header
        self.header = Header("Metadata", self)
        self.layout().addWidget(self.header)

        # content
        self.content = QWidget(self)
        self.content.setLayout(QVBoxLayout())
        self.content.layout().setAlignment(Qt.AlignTop)
        self.content.layout().setSpacing(10)
        self.content.layout().setContentsMargins(20, 0, 20, 0)

        for i, t in enumerate(IMPORTANT_METADATA):
            self.content.layout().addWidget(InputWithLabel(t, self))
            self.content.layout().itemAt(i).widget().set_input(QSuggestionWidget(self, AVAILABLE_INFO))

        self.layout().addWidget(self.content)

        self.load_config()

    def get_processor(self):
        data = {}

        on = False
        for i in range(self.content.layout().count()):
            widget = self.content.layout().itemAt(i).widget()
            if widget.get_input() != '':
                on = True
                data[widget.get_name().replace('_', '')] = widget.get_input()
                print(self.content.layout().itemAt(i).widget().get_input())

        if not on:
            return MetadataPostProcessor(on=False)

        print(data)

        return MetadataPostProcessor(data)

    def load_config(self):
        for i in range(self.content.layout().count()):
            widget = self.content.layout().itemAt(i).widget()
            f_text = widget.get_name().replace(' ', '_').lower()
            val = getattr(settings.ytdl, f_text).get()
            if val is not None:
                widget.input.setText(val)

    def save_config(self):
        for i in range(self.content.layout().count()):
            widget = self.content.layout().itemAt(i).widget()
            f_text = widget.get_name().replace(' ', '_').lower()
            getattr(settings.ytdl, f_text).set(widget.get_input())
