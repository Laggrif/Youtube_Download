import logging

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QVBoxLayout, QWidget, QRadioButton

from src.components.headerwithlinewidget import Header
from src.components.inputwithlabelwidget import InputWithLabel
import src.Config as config


# save on exit
# minimize to tray if downloading
# automatically delete completed downloads
# save cookies
# save history
# save path

class SettingsWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        if hasattr(parent, 'config_category'):
            self.config_category = parent.config_category.copy()
            self.config_category.append('Settings')
        else:
            self.config_category = 'Settings'
        self.setObjectName("SettingsWidget")
        self.setLayout(QVBoxLayout())
        self.layout().setAlignment(Qt.AlignTop)
        self.layout().setSpacing(0)

        # header
        self.header = Header("General settings", self)
        self.layout().addWidget(self.header)

        # content
        self.content = QWidget(self)
        self.content.setLayout(QVBoxLayout())
        self.content.layout().setAlignment(Qt.AlignTop)
        self.content.layout().setSpacing(10)
        self.content.layout().setContentsMargins(20, 0, 20, 0)

        self.contents = {"Save on exit": [], "Minimize to tray": [], "Delete completed downloads": [],
                         "Save cookies": [], "Save history": [], "Save download path": []}

        for i, text in enumerate(self.contents):
            widget = InputWithLabel(text, self)
            f_text = text.replace(' ', '_').lower()
            widget.setObjectName(f"yt_{f_text}")
            checkbox = QRadioButton(self)
            checkbox.setFixedWidth(15)
            checkbox.setFixedHeight(15)
            widget.set_input(checkbox)
            widget.label.setFixedWidth(200)
            self.contents[text].append(widget)
            self.contents[text].append(f_text)
            self.content.layout().addWidget(widget)
            try:
                val = config.get(f_text, self.config_category)
                widget.input.setChecked(val == "true")
            except KeyError:
                pass

        self.contents["Save on exit"][0].input.setChecked(
            config.get("save_on_exit", self.config_category[:1]) == "true")
        self.contents["Save on exit"][0].input.clicked.connect(self.toggle_save)

        self.layout().addWidget(self.content)

    def toggle_save(self):
        config.put("save_on_exit", self.contents["Save on exit"][0].input.isChecked(), self.config_category[:-1])
        logging.debug("Save on exit: %s", self.contents["Save on exit"][0].input.isChecked())

    def save_config(self):
        for v in list(self.contents.values()):
            if v[0].get_name() != "Save on exit":
                config.put(v[1], v[0].input.isChecked(), self.config_category)
