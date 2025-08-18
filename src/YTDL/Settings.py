import logging

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QVBoxLayout, QWidget, QRadioButton

from src.components.headerwithlinewidget import Header
from src.components.inputwithlabelwidget import InputWithLabel
from src.Config import settings
from src.YTDL.Browser import YoutubeBrowser


# save on exit
# minimize to tray if downloading
# automatically delete completed downloads
# save cookies
# save history
# save path

class SettingsWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
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
                         "Save cookies": [], "Save history": [], "Save path": []}

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
                if f_text == "save_on_exit":
                    val = settings.save_on_exit.get()
                else:
                    val = getattr(settings.ytdl, f_text).get()
                widget.input.setChecked(val)
            except KeyError:
                pass

        self.contents["Save cookies"][0].input.clicked.connect(self.toggle_save_cookies)
        self.contents["Save history"][0].input.clicked.connect(self.toggle_save_history)
        self.contents["Save on exit"][0].input.clicked.connect(self.toggle_save)
        self.contents["Minimize to tray"][0].input.clicked.connect(self.toggle_minimize_to_tray)
        self.contents["Delete completed downloads"][0].input.clicked.connect(self.toggle_delete_completed_downloads)

        self.old_minimize_to_tray = self.contents["Minimize to tray"][0].input.isChecked()
        self.old_delete_completed_downloads = self.contents["Delete completed downloads"][0].input.isChecked()

        self.layout().addWidget(self.content)

    def toggle_save_cookies(self):
        YoutubeBrowser.save_cookies = self.contents["Save cookies"][0].input.isChecked()

    def toggle_save_history(self):
        YoutubeBrowser.save_history = self.contents["Save history"][0].input.isChecked()

    def toggle_save(self):
        settings.save_on_exit.set(self.contents["Save on exit"][0].input.isChecked())
        logging.debug("Save on exit: %s", self.contents["Save on exit"][0].input.isChecked())

    def toggle_minimize_to_tray(self):
        settings.ytdl.minimize_to_tray.set(self.contents["Minimize to tray"][0].input.isChecked())

    def toggle_delete_completed_downloads(self):
        settings.ytdl.delete_completed_downloads.set(self.contents["Delete completed downloads"][0].input.isChecked())

    def restore_config(self):
        print("restoring config")
        settings.ytdl.minimize_to_tray.set(self.old_minimize_to_tray)
        settings.ytdl.delete_completed_downloads.set(self.old_delete_completed_downloads)

    def save_config(self):
        print(self.contents["Delete completed downloads"][0].input.isChecked())
        for v in list(self.contents.values()):
            if v[0].get_name() != "Save on exit":
                getattr(settings.ytdl, v[1]).set(v[0].input.isChecked())
