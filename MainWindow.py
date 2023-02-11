import sys

from PySide6.QtGui import QResizeEvent
from PySide6.QtWidgets import QMainWindow, QApplication, QStackedWidget, QFrame, QPushButton

from config import save_config


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        geometry = QApplication.primaryScreen().availableGeometry()

        self.setGeometry(geometry.width() / 2 - 350, geometry.height() / 2 - 200, 700, 400)
        self.setWindowTitle("Youtube Downloader and more :)")

        self.stack = QStackedWidget(self)
        self.stack.resize(self.width(), self.height())
        self.stack.show()

        self.views = {}

        self.home_view = Home(self.stack, self)
        self.views[self.home_view] = self.stack.count()
        self.stack.addWidget(self.home_view)

    def add_view(self, view):
        self.views[view] = self.stack.count()
        self.stack.addWidget(view)
        self.home_view.add_view(view)

    def change_view(self, view):
        view.show()
        self.stack.setCurrentIndex(self.views[view])

    def home(self):
        self.change_view(self.home_view)

    def resizeEvent(self, event: QResizeEvent):
        event.accept()
        self.stack.resize(self.width(), self.height())
        self.home_view.resize(self.width(), self.height())
        for view in list(self.views.keys()):
            view.resize(self.width(), self.height())

    def closeEvent(self, event):
        save_config()
        event.accept()
        sys.exit(0)


class Home(QFrame):

    def __init__(self, parent, main_window: MainWindow):
        super().__init__()
        self.main_window = main_window
        self.setObjectName('Home')
        self.name = 'home'
        self.setParent(parent)
        self.resize(parent.width(), parent.height())

    def add_view(self, view):
        button = QPushButton(view.name)
        button.setParent(self)

        def switch_view():
            self.parent().parent().change_view(view)

        button.clicked.connect(switch_view)
        button.adjustSize()
        button.resize(button.width(), 35)
        button.move(int((self.width() - button.width()) / 2), 30 + (self.parent().count() - 2) * 45)
        button.show()

        self.setMinimumHeight((self.parent().count() - 1) * 45 + 30 + 20)
        self.setMinimumWidth(max(self.main_window.minimumWidth(), button.width() + 60))
        self.show()

    def resizeEvent(self, event: QResizeEvent):
        event.accept()
        self.resize(self.parent().width(), self.parent().height())
        for child in self.children():
            child.move(int((self.width() - child.width()) / 2), child.pos().y())

    def show(self):
        super().show()
        self.main_window.setMinimumHeight(self.minimumHeight())
        self.main_window.setMinimumWidth(self.minimumWidth())


class View(QFrame):
    def __init__(self, parent, name):
        super().__init__()
        self.setParent(parent)
        self.name = name

        self.button = QPushButton('Home')
        self.button.setParent(self)
        self.button.clicked.connect(self.home)
        self.button.setGeometry(10, 10, 0, 0)
        self.button.adjustSize()
        self.button.show()

    def home(self):
        self.parent().parent().home()
