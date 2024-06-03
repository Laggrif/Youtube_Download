from PySide6.QtCore import Qt
from PySide6.QtGui import QFocusEvent
from PySide6.QtWidgets import QVBoxLayout, QWidget, QLabel, QLineEdit, QPushButton, QListWidget


class QSuggestionWidget(QWidget):
    def __init__(self, parent, suggestions):
        super().__init__(parent)
        self.suggestions = suggestions
        self.setLayout(QVBoxLayout())
        self.layout().setAlignment(Qt.AlignTop)
        self.layout().setSpacing(0)

        self.text = QLineEdit(self)
        self.text.setFixedWidth(self.width())
        self.text.setFixedHeight(20)
        self.text.textChanged.connect(self.keyPressed)
        self.text.selectionChanged.connect(self.selectionHandler)
        self.layout().addWidget(self.text)

        self.suggestion_widget = QListWidget()
        self.suggestion_widget.setVisible(False)
        self.suggestion_widget.setLayout(QVBoxLayout())
        self.suggestion_widget.layout().setAlignment(Qt.AlignTop)
        self.suggestion_widget.layout().setSpacing(0)
        self.suggestion_widget.layout().setContentsMargins(0, 0, 0, 0)
        self.suggestion_widget.setFixedWidth(self.width())
        self.suggestion_widget.setMaximumHeight(100)
        self.suggestion_widget.hide()
        self.suggestion_widget.itemClicked.connect(self.on_suggestion_clicked)
        self.suggestion_widget.adjustSize()

        self.layout().addWidget(self.suggestion_widget)

    def selectionHandler(self):
        if self.hasFocus() or self.text.hasFocus():
            self.keyPressed()
        else:
            self.suggestion_widget.setVisible(False)
            self.suggestion_widget.hide()

    def keyPressed(self):
        self.suggestion_widget.clear()
        for i in self.suggestions:
            if self.text.text() == "" or i.startswith(self.text.text()):
                print(i)
                self.suggestion_widget.addItem(i)
        self.suggestion_widget.setVisible(True)
        self.suggestion_widget.show()
        self.suggestion_widget.adjustSize()
        self.adjustSize()
        self.parent().adjustSize()

    def on_suggestion_clicked(self, arg__1):
        self.text.setText(arg__1.text())
