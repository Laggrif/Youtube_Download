import math

from PySide6.QtCore import Qt, QPoint, QEvent
from PySide6.QtGui import QFocusEvent, QMoveEvent, QPaintEvent, QMouseEvent, QColor, QKeyEvent
from PySide6.QtWidgets import QVBoxLayout, QWidget, QLineEdit, QListWidget, QApplication

from src.components.inputwithlabelwidget import InputWithLabel


class QSuggestionWidget(QLineEdit):
    def __init__(self, parent, suggestions):
        super().__init__(parent)
        self.suggestions = suggestions

        self.textChanged.connect(self.keyPressed)
        self.selectionChanged.connect(self.selectionHandler)
        self.installEventFilter(self)

        self.suggestion_widget = QListWidget(self.topLevelWidget())
        self.suggestion_widget.setObjectName('SuggestionWidgetList')
        self.suggestion_widget.setVisible(False)
        self.suggestion_widget.setLayout(QVBoxLayout())
        self.suggestion_widget.layout().setAlignment(Qt.AlignTop)
        self.suggestion_widget.layout().setSpacing(0)
        self.suggestion_widget.layout().setContentsMargins(0, 0, 0, 0)
        self.suggestion_widget.setFixedWidth(self.width())
        self.suggestion_widget.setMaximumHeight(70)
        self.suggestion_widget.adjustSize()
        self.suggestion_widget.hide()

        self.suggestion_widget.itemClicked.connect(self.on_suggestion_clicked)
        self.install_event_filters(self)

    def selectionHandler(self):
        if self.hasFocus():
            self.keyPressed()
        else:
            self.suggestion_widget.setVisible(False)
            self.suggestion_widget.hide()

    def keyPressed(self):
        self.suggestion_widget.clear()
        self.suggestion_widget.adjustSize()

        p = self.mapToGlobal(self.rect().topLeft())
        p = self.topLevelWidget().mapFromGlobal(p)
        self.suggestion_widget.move(p.x(), p.y() + self.height())

        starting_bracket = math.inf
        cursor_pos = self.cursorPosition()
        for i in range(0, cursor_pos):
            if self.text()[i] == '{':
                starting_bracket = i
            elif self.text()[i] == '}':
                starting_bracket = math.inf

        if starting_bracket == math.inf:
            return

        c = 0
        input = self.text()[starting_bracket + 1:cursor_pos]
        for i in self.suggestions:
            if input in i or i == input:
                self.suggestion_widget.addItem(i)
                c += 1

        self.suggestion_widget.raise_()
        self.suggestion_widget.setVisible(True)
        self.suggestion_widget.show()
        self.suggestion_widget.setFixedHeight(min(c * 20 + 6, 70))
        self.adjustSize()
        self.parent().adjustSize()

    def on_suggestion_clicked(self, arg__1):
        pos = -1
        for i in range(self.cursorPosition() - 1, -1, -1):
            if self.text()[i] == '{':
                pos = i
                break
        text = self.text()
        closing = 0
        for i in range(self.cursorPosition(), len(text)):
            if text[i] == '{':
                closing = 0
                break
            elif text[i] == '}':
                closing = i
                break

        if closing:
            self.setText(text[:pos + 1] + arg__1.text() + text[closing:])
        else:
            self.setText(text[:pos + 1] + arg__1.text() + '}' + text[self.cursorPosition():])
        self.suggestion_widget.setVisible(False)

    def eventFilter(self, obj, event):
        if event.type() == QFocusEvent.FocusOut:
            self.suggestion_widget.setVisible(False)
            self.suggestion_widget.hide()
        elif event.type() == QFocusEvent.FocusIn:
            if obj == self or obj == self.suggestion_widget:
                self.keyPressed()
        elif type(event) == QPaintEvent:
            p = self.mapToGlobal(self.rect().topLeft())
            p = self.topLevelWidget().mapFromGlobal(p)
            self.suggestion_widget.move(p.x(), p.y() + self.height())
        elif event.type() == QMouseEvent.MouseButtonPress:
            if obj != self.suggestion_widget and obj != self:
                self.suggestion_widget.setVisible(False)
                self.suggestion_widget.hide()
                self.clearFocus()
            else:
                self.keyPressed()

        elif event.type() == QKeyEvent.KeyRelease:
            if event.key() == Qt.Key_Escape:
                self.suggestion_widget.setVisible(False)
                self.suggestion_widget.hide()
                self.clearFocus()
            elif ((event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter)
                  and self.suggestion_widget.selectedItems() != []):
                self.on_suggestion_clicked(self.suggestion_widget.selectedItems()[0])
                self.clearFocus()
            elif self.suggestion_widget.count() > 0:
                if event.key() == Qt.Key_Down:
                    self.suggestion_widget.setCurrentRow(
                        (self.suggestion_widget.currentRow() + 1) % self.suggestion_widget.count())
                elif event.key() == Qt.Key_Up:
                    if self.suggestion_widget.currentRow() == -1:
                        self.suggestion_widget.setCurrentRow(self.suggestion_widget.count() - 1)
                    else:
                        self.suggestion_widget.setCurrentRow(
                            (self.suggestion_widget.currentRow() - 1) % self.suggestion_widget.count())
        return super().eventFilter(obj, event)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.setFixedWidth(self.width())
        self.suggestion_widget.setFixedWidth(self.width())
        self.adjustSize()

    def install_event_filters(self, widget):
        # TODO find a better way of doing this
        widget.installEventFilter(self)
        if widget.parent():
            self.install_event_filters(widget.parent())


if __name__ == "__main__":
    app = QApplication()

    window = QWidget()
    window.setGeometry(500, 500, 300, 500)
    window.setLayout(QVBoxLayout())
    window.layout().setAlignment(Qt.AlignTop)
    window.layout().setSpacing(0)
    window.setStyleSheet("margin: 0; padding: 0;")

    title = QSuggestionWidget(window, ["title1", "title2", "title3"])
    t = InputWithLabel("Title", window)
    t.set_input(title)
    window.layout().addWidget(t)

    t2 = QSuggestionWidget(window, ["title1", "title2", "title3", "t4", "alb", "rasd", "rasd"])
    ti2 = InputWithLabel("Title", window)
    ti2.set_input(t2)
    window.layout().addWidget(ti2)

    window.show()
    app.exec()
