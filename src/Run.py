import os
import sys

from PySide6.QtCore import QDir
from PySide6.QtWidgets import QApplication

from src.MainWindow import MainWindow, View
from src.YTDL import YTDL
from src.Directory import application_path
from os.path import join


def main():
    app = QApplication(sys.argv)

    QDir.addSearchPath('icon', join(application_path, "res", "icon"))
    with open(join(application_path, "res", "style.qss"), "r") as f:
        _style = f.read()
        app.setStyleSheet(_style)

    window = MainWindow()
    window.show()

    stack = window.stack

    Directory = View(stack, 'Directory')
    window.add_view(Directory)

    ytdl = YTDL(stack, window)
    window.add_view(ytdl)

    sys.exit(app.exec())


if __name__ == '__main__':
    main()
