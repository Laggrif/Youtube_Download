from PySide6.QtGui import QPainter, QPen, QColor, QBrush
from PySide6.QtWidgets import QWidget


class ScrollBar(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.setVisible(True)
        self.color = (40, 40, 40)
        self.pressed = False
        self.grabCoord = 0
        self.view = None

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        self.pressed = True
        self.grabCoord = event.y()

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        self.pressed = False

    def mouseMoveEvent(self, event):
        if self.pressed:
            new = self.y() + event.y() - self.grabCoord
            if new < 0:
                self.move(self.x(), 0)
                self.view.move(self.view.x(), 0)
            elif new > self.parent().height() - self.height():
                self.move(self.x(), self.parent().height() - self.height())
                self.view.move(self.view.x(), self.parent().height() - self.view.height())
            else:
                self.move(self.x(), new)
                self.view.move(self.view.x(), - int(self.parent().height() * self.pos().y() / self.height()))

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setPen(QPen(QColor(*self.color), 1))
        painter.setBrush(QBrush(QColor(*self.color)))
        painter.drawRoundedRect(0, 0, self.width(), self.height(), 5, 5)
