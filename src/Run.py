import logging
import sys
import argparse

from PySide6.QtCore import QDir
from PySide6.QtWidgets import QApplication

from src.MainWindow import MainWindow, View
from src.YTDL.Window import YTDL
from src.Directory import application_path
from os.path import join
from src.StyleSheetParser import get_style

VERSION = '0.1.0'


def main():
    app = QApplication(sys.argv)

    QDir.addSearchPath('icon', join(application_path, "res", "icon"))
    app.setStyle(get_style())

    window = MainWindow()
    window.show()

    stack = window.stack

    Directory = View(stack, 'Directory')
    window.add_view(Directory)

    ytdl = YTDL(stack, window)
    window.add_view(ytdl)

    window.setMinimumWidth(window.width() - 100 - 20)

    sys.exit(app.exec())


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--version', action='store_true', help='Print the version of the program')
    parser.add_argument('--debug', action='store_true', help='Print debug messages')

    args = parser.parse_args()

    if args.version:
        print(VERSION)
        sys.exit(0)

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

    main()
