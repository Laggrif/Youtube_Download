from PySide6.QtWidgets import QLabel, QWidget, QFrame, QGridLayout


class Header(QWidget):
    def __init__(self, title, parent=None):
        super().__init__(parent=parent)
        self.setStyleSheet("margin: 0; padding: 0;")
        
        header = QLabel(title, self)
        line = QFrame(self)
        line.setStyleSheet("margin: 0 -5px 0 -5px; color: #c9c9c9;")
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Plain)
        line.setLineWidth(0)
        line.setMidLineWidth(0)

        self.header_layout = QGridLayout()
        self.header_layout.setSpacing(5)
        self.header_layout.addWidget(header)
        self.header_layout.addWidget(line)

        self.setLayout(self.header_layout)

