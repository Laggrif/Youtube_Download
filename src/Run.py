import sys

from PySide6.QtCore import QDir, QFile
from PySide6.QtWidgets import QApplication

from MainWindow import MainWindow, View
from YTDL import YTDL
from Directory import application_path

from PySide6 import QtWebEngineWidgets, QtWebEngineCore
import yt_dlp

app = QApplication(sys.argv)

QDir.addSearchPath('icon', application_path + "\\res\\icon")
with open(application_path + "\\res\\style.qss", "r") as f:
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
