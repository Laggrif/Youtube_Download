from os.path import join
from os import chdir, getcwd

from PySide6.QtCore import Qt, QTime
from PySide6.QtWidgets import QWidget, QPushButton, QListWidget, QGridLayout, QDialog, QVBoxLayout, QLineEdit, QLabel, \
    QComboBox, QHBoxLayout, QLayout, QRadioButton, QSpacerItem, QSizePolicy, QFormLayout, QDateTimeEdit

from src.components.suggestionwidget import QSuggestionWidget
if getcwd().endswith("components"):
    application_path = join(getcwd(), "..")
else:
    from src.Directory import application_path


TYPE_TO_DESCRIPTION = {
    "Metadata": "Metadata postprocessor",
    "Duration": "Duration limit",
    "Converter": "Format converter",
    "Playlist": "Playlist inclusion"
}

DESCRIPTION_TO_TYPE = {}
for k, v in TYPE_TO_DESCRIPTION.items():
    DESCRIPTION_TO_TYPE[v] = k


class ModifiableList(QWidget):
    def __init__(self, parent, popup=None):
        super().__init__(parent)
        self.setVisible(True)
        self.setObjectName("ModifiableListWidget")
        with open(join(application_path, "res", "style.qss"), "r") as f:
            _style = f.read()
            self.setStyleSheet(_style)

        self.popup_name = popup
        self.popup = None
        self.filters = {}

        self.setLayout(QGridLayout())
        self.layout().setSpacing(0)

        self.add_button = QPushButton("+", self)
        self.add_button.clicked.connect(self.add_item)
        self.add_button.setObjectName("ModifiableListWidgetButton")
        self.add_button.setStyleSheet("border-top-right-radius: 5px; border-bottom: 0;")

        self.edit_button = QPushButton("🖉", self)
        self.edit_button.clicked.connect(self.edit_item)
        self.edit_button.setObjectName("ModifiableListWidgetButton")
        self.edit_button.setStyleSheet("border-bottom: 0;")

        self.remove_button = QPushButton("-", self)
        self.remove_button.clicked.connect(self.remove_item)
        self.remove_button.setObjectName("ModifiableListWidgetButton")
        self.remove_button.setStyleSheet("border-bottom-right-radius: 5px;")

        self.list_widget = QListWidget(self)
        self.list_widget.setStyleSheet(self.styleSheet())
        self.list_widget.setObjectName("ModifiableListWidgetList")
        self.list_widget.setAlternatingRowColors(True)
        self.list_widget.setSortingEnabled(True)
        self.list_widget.setFixedHeight(140)

        self.layout().addWidget(self.list_widget, 0, 0, 4, 1)
        self.layout().addWidget(self.add_button, 1, 1)
        self.layout().addWidget(self.edit_button, 2, 1)
        self.layout().addWidget(self.remove_button, 3, 1)

    def add_item(self):
        self.popup = getattr(
            __import__("src.components.modifiablelistwidget", fromlist=[self.popup_name]), self.popup_name)(self)
        self.popup.exec()

    def edit_item(self):
        name = self.list_widget.currentItem().text()
        self.popup = getattr(
            __import__("src.components.modifiablelistwidget", fromlist=[self.popup_name]), self.popup_name)(self)
        self.popup.set_edit(name)
        self.popup.exec()

    def remove_item(self):
        name = self.list_widget.takeItem(self.list_widget.currentRow()).text()
        self.filters.pop(name)

    def process_popup(self, data, edit=False, name=None):
        if data["name"] in self.filters and data["name"] != name:
            data["name"] = data["name"].rsplit("(", 1)[0]

            if data["name"] in self.filters and data["name"] != name:
                num = 1
                while data["name"] + f"({num})" in self.filters and data["name"] + f"({num})" != name:
                    num += 1
                data["name"] += f"({num})"

        if edit:
            del self.filters[name]
            self.filters[data["name"]] = data["data"]
            self.list_widget.currentItem().setText(data["name"])
        else:
            self.list_widget.addItem(data["name"])
            self.filters[data["name"]] = data["data"]


class FilterPopup(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.return_data = {}
        self.edit = False
        self.edit_name = None
        self.setFixedSize(0, 0)
        self.setMinimumWidth(250)

        self.setModal(True)
        self.setObjectName("FilterPopup")

        self.setLayout(QVBoxLayout())

        self.filter_name = QComboBox(self)
        self.filter_name.addItems(["Select filter", "Metadata", "Duration", "Converter", "Playlist"])
        self.filter_name.setObjectName("FilterPopupComboBox")
        self.filter_name.currentIndexChanged.connect(self.change_content)

        self.central_widget = QWidget(self)

        confirm_button = QPushButton("OK", self)
        confirm_button.setMaximumWidth(100)
        confirm_button.clicked.connect(self.confirm)

        cancel_button = QPushButton("Cancel", self)
        cancel_button.setMaximumWidth(100)
        cancel_button.clicked.connect(self.close)

        spacer_l = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)
        spacer_m = QSpacerItem(100, 0, QSizePolicy.Preferred, QSizePolicy.Minimum)
        spacer_r = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)

        buttons_widget = QWidget(self)
        buttons_widget.setLayout(QHBoxLayout())
        buttons_widget.layout().addItem(spacer_l)
        buttons_widget.layout().addWidget(cancel_button)
        buttons_widget.layout().addItem(spacer_m)
        buttons_widget.layout().addWidget(confirm_button)
        buttons_widget.layout().addItem(spacer_r)

        self.layout().addWidget(self.filter_name)
        self.layout().addWidget(self.central_widget)
        self.layout().addItem(QSpacerItem(0, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        self.layout().addWidget(buttons_widget)
        self.layout().setSpacing(30)

        self.filter_name.setCurrentIndex(0)

    def change_content(self):
        filter_index = self.filter_name.currentIndex()
        if self.central_widget is not None:
            self.layout().removeWidget(self.central_widget)
            self.central_widget.setParent(None)
            self.central_widget.deleteLater()
            self.central_widget = None
        match filter_index:
            case 1:
                self.metadata()
            case 2:
                self.duration()
            case 3:
                self.converter()
            case 4:
                self.playlist()
            case _:
                self.none()
        self.adjustSize()
        if self.central_widget:
            self.layout().insertWidget(1, self.central_widget)

    def none(self):
        self.central_widget = QWidget(self)
        self.return_data = None

    def metadata(self):
        self.central_widget = QWidget(self)
        self.central_widget.setLayout(QFormLayout())

        self.central_widget.layout().addRow("title", QSuggestionWidget(self, ["title", "artist", "album", "genre"]))

        self.return_data = {"name": TYPE_TO_DESCRIPTION["Metadata"],
                            "data": {
                                "type": "Metadata"}}

    def duration(self):
        self.central_widget = QWidget(self)
        self.central_widget.setLayout(QFormLayout())

        from_ = QDateTimeEdit(QTime(), self)
        from_.setDisplayFormat("hh:mm:ss")
        to_ = QDateTimeEdit(QTime(9999, 59, 59), self)
        to_.setDisplayFormat("hh:mm:ss")

        container = QWidget(self)
        container.setStyleSheet("margin: 0; padding: 0;")
        container.setLayout(QFormLayout())
        container.layout().addRow("From", from_)
        container.layout().addRow("To", to_)

        self.central_widget.layout().addRow("Duration limit:", container)

        self.return_data = {"name": TYPE_TO_DESCRIPTION["Duration"],
                            "data": {"type": "Duration"}}

    def converter(self):
        convert_to = QComboBox(self)
        convert_to.setObjectName("FilterPopupComboBox")
        convert_to.addItems(["mp3", "wav", "flac", "m4a"])

        keep_original = QRadioButton("", self)

        self.central_widget = QWidget(self)
        self.central_widget.setLayout(QFormLayout())
        self.central_widget.layout().setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        self.central_widget.layout().setVerticalSpacing(20)
        self.central_widget.layout().addRow("format", convert_to)
        self.central_widget.layout().addRow("keep original", keep_original)
        self.return_data = {"name": TYPE_TO_DESCRIPTION["Converter"],
                            "data": {"type": "Converter",
                                     "convert_to": convert_to.currentIndex(),
                                     "keep_original": keep_original.isChecked()}}

    def playlist(self):
        checkbox = QRadioButton("Include Playlists", self)
        checkbox.setObjectName("FilterPopupCheckBox")
        checkbox.setChecked(True)
        self.central_widget = checkbox
        self.return_data = {"name": TYPE_TO_DESCRIPTION["Playlist"],
                            "data": {"type": "Playlist", "include": checkbox.isChecked()}}

    def confirm(self):
        if self.return_data is None:
            self.close()
            return
        if self.edit:
            self.parent().process_popup(self.return_data, edit=True, name=self.edit_name)
        else:
            self.parent().process_popup(self.return_data)
        self.close()

    def set_edit(self, name):
        self.edit_name = name
        self.edit = True
        self.filter_name.setCurrentIndex(self.filter_name.findText(DESCRIPTION_TO_TYPE[name.rsplit("(", 1)[0]]))
        self.change_content()
        self.change_content()


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication, QMainWindow
    from os import chdir

    chdir("..")

    app = QApplication([])
    mainwin = QMainWindow()
    widget = ModifiableList(mainwin, "FilterPopup")
    mainwin.setCentralWidget(widget)
    mainwin.show()
    app.exec()
