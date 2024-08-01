from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGridLayout, QLineEdit, QLabel, QWidget

from src.StyleSheetParser import get_style


class InputWithLabel(QWidget):
    def __init__(self, label, parent=None):
        super().__init__(parent=parent)
        self.setStyleSheet("margin: 0; padding: 0;")

        self.label = QLabel(label, self)
        self.label.setFixedWidth(120)
        self.input = QLineEdit(self)

        self.layout = QGridLayout()
        self.layout.addWidget(self.label, 0, 0)
        self.layout.addWidget(self.input, 0, 1)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setAlignment(Qt.AlignLeft)

        self.setLayout(self.layout)

    def set_input(self, widget: QWidget):
        self.layout.removeWidget(self.input)
        self.input.deleteLater()
        self.input = widget
        self.layout.addWidget(self.input, 0, 1)

    def set_label(self, label):
        self.layout.removeWidget(self.label)
        self.label.deleteLater()
        self.label = label
        self.layout.addWidget(self.label, 0, 0)

    def get_input(self):
        try:
            return self.input.text()
        except AttributeError:
            return None

    def get_name(self):
        return self.label.text()

    def setDisabled(self, arg__1):
        if arg__1:
            self.label.setStyleSheet("color: #808080;")
            self.input.setStyleSheet("color: #808080; background-color: #efefef; border: 1px solid #c4c4c4;")
        else:
            self.label.setStyleSheet(get_style())
            self.input.setStyleSheet(get_style())
        super().setDisabled(arg__1)
