import sys

from PySide6.QtWidgets import QApplication

from MainWindow import MainWindow, View
from YTDL import YTDL

from PySide6 import QtWebEngineWidgets, QtWebEngineCore
import yt_dlp

app = QApplication(sys.argv)

with open("./style.qss", "r") as f:
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
