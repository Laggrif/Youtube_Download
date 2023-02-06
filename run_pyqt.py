import os.path
import re

import time

import sys
from yt_dlp.utils import parse_filesize, format_bytes

from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *

from Youtube_music_downloader import DownloadThread


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        geometry = QApplication.primaryScreen().availableGeometry()

        with open("style.qss", "r") as f:
            _style = f.read()
            app.setStyleSheet(_style)
        self.setGeometry(geometry.width() / 2 - 350, geometry.height() / 2 - 200, 700, 400)
        self.setWindowTitle("Youtube Downloader and more :)")

        self.stack = QStackedWidget(self)
        self.stack.resize(self.width(), self.height())
        self.stack.show()

        self.views = {}

        self.home_view = Home(self.stack)
        self.views[self.home_view.name] = self.stack.count()
        self.stack.addWidget(self.home_view)

    def add_view(self, view):
        self.views[view.name] = self.stack.count()
        self.stack.addWidget(view)
        self.home_view.add_view(view)

    def change_view(self, view):
        self.stack.setCurrentIndex(self.views[view.name])

    def home(self):
        self.change_view(self.home_view)


class Home(QWidget):

    def __init__(self, parent):
        super().__init__()
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


class View(QWidget):
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


class YTDL(View):
    def __init__(self, parent):
        super().__init__(parent, 'Youtube Download')
        self.downloads = {}

        # Dimensions of main window
        self.WIDTH = parent.width()
        self.HEIGHT = parent.height()

        # Input for url and its label
        self.download_input = QLineEdit(self)
        self.download_input.setObjectName('download_input')
        self.download_input.setGeometry(40, 80, self.WIDTH - 80 - 24, 24)
        self.download_input_label = QLabel('Input a youtube url', self)
        self.download_input_label.setObjectName('input_label')
        self.download_input_label.adjustSize()
        self.download_input_label.setGeometry(40 + 5, 80 - 20, self.download_input_label.width(), 20)
        # Button to clear url input
        self.clear_button = QPushButton('', self)
        close_icon = self.style().standardIcon(QStyle.SP_TitleBarCloseButton)
        self.clear_button.setIcon(close_icon)
        self.clear_button.setObjectName('clear_button')
        self.clear_button.setGeometry(self.download_input.pos().x() + self.download_input.width(),
                                      self.download_input.pos().y(),
                                      24,
                                      24)
        self.clear_button.clicked.connect(self.clear)

        # Input for path and its label
        self.path_input = QLineEdit(self)
        self.path_input.setText(os.path.dirname(__file__))
        self.path_input.setGeometry(60, 140, self.WIDTH - 120 - 80, 24)
        self.path_input_label = QLabel('Output path', self)
        self.path_input_label.setObjectName('input_label')
        self.path_input_label.adjustSize()
        self.path_input_label.setGeometry(60 + 5, 140 - 20, self.path_input_label.width(), 20)
        # Button to browse file explorer
        self.path_button = QPushButton('Browse', self)
        self.path_button.setObjectName('path_button')
        self.path_button.move(self.path_input.pos().x() + self.path_input.width() + 5,
                              self.path_input.pos().y())
        self.path_button.resize(self.WIDTH - self.path_button.pos().x() - 60, 24)
        self.path_button.clicked.connect(self.file_explorer)

        # Button to download inserted url
        self.download_button = QPushButton('Download', self)
        self.download_button.setGeometry(int((self.WIDTH - 100) / 2), 200, 100, 30)
        self.download_button.clicked.connect(self.download)

        # Layout for output
        self.output_vbox = QVBoxLayout(self)
        self.output_vbox.setAlignment(Qt.AlignmentFlag.AlignTop)
        # Widget containing output
        self.output_widget = QWidget(self)
        self.output_widget.setLayout(self.output_vbox)
        self.output_widget.setStyleSheet("background-color : grey;")
        # Scroll manager for output
        self.output_scroll = QScrollArea(self)
        self.output_scroll.setGeometry(0, 250, self.WIDTH, self.HEIGHT - 250)
        self.output_scroll.setWidgetResizable(True)
        self.output_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.output_scroll.setWidget(self.output_widget)

    def clear(self):
        self.download_input.setText('')

    def file_explorer(self):
        path = QFileDialog.getExistingDirectory(None,
                                                'Select a folder',
                                                self.path_input.text(),
                                                QFileDialog.ShowDirsOnly)
        if path != '':
            self.path_input.setText(path)

    def download(self):
        if self.download_input.text() != '':
            th = QThread(None)
            worker = DownloadThread(self.download_input.text(), self.path_input.text(), len(self.downloads))
            worker.moveToThread(th)
            th.worker = worker
            th.started.connect(worker.run)
            worker.finished.connect(th.quit())
            worker.sig.connect(self.process_signal)

            self.downloads[len(self.downloads)] = [th, self.add_download_widget()]
            th.start()

            self.download_input.setText('')

    def process_signal(self, signal):
        id = signal[0]
        widget = self.downloads[id][1]
        signal = signal[1]
        if len(signal) == 2 and not isinstance(signal, str):
            return
        elif isinstance(signal, str):
            if signal.startswith('Delete'):
                self.downloads[id][0].quit()
                self.downloads[id][0].wait()
                widget.deleteLater()
                del self.downloads[id]

            elif signal.startswith('Extracting'):
                pass

            elif signal.startswith('Name'):
                widget.update_name(signal.split(': ')[1])

            elif signal.startswith('Destination'):
                widget.update_name(signal.split(': ')[1])
                widget.update_progress(100)
                widget.update_status('Converting to mp3')

            elif signal.startswith('Already downloaded'):
                size = signal.split(': ')[1]
                widget.set_size(size)
                widget.update_progress(100)

        elif isinstance(signal, list):
            if len(signal) == 4:
                widget.set_size(signal[3])
                widget.update_progress(float(signal[0].replace('%', '')), signal[1])

        self.output_scroll.update()

    def add_download_widget(self):
        widget = ProgressWidget(self.output_widget, self.output_vbox, len(self.downloads), self.download_input.text())

        return widget

    def updateGeometry(self):
        super().updateGeometry()
        self.WIDTH = self.parent.width()
        self.HEIGHT = self.parent.height()
        self.download_input.setGeometry(40, 80, self.WIDTH - 80 - 100, 50)
        self.download_button.setGeometry(self.WIDTH - 40 - 90, 80, self.WIDTH - 90 - self.download_input.width(), 22)
        self.clear_button.setGeometry(self.WIDTH - 40 - 90, 130 - 22, 90, 22)
        # TODO update sizes based on window size


class ProgressWidget(QFrame):
    def __init__(self, output_widget, output_vbox, pos, url):
        super().__init__(output_widget)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setObjectName('ProgressWidget')
        with open("style.qss", "r") as f:
            _style = f.read()
            self.setStyleSheet(_style)

        self.time = time.time()
        self.size = ''
        self.speed = []

        self.output_widget = output_widget
        self.output_vbox = output_vbox

        x = 20
        y = 10 + pos * 40

        self.setGeometry(x, y, self.output_widget.width() - 2 * x, 50)
        self.setFixedHeight(50)

        self.output_vbox.addWidget(self)

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setValue(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setGeometry(self.width() - 200, 5, 200, 20)

        self.download_name = QLabel('Fetching video name...', self)
        self.download_name.move(5, 5)
        self.download_name.setMaximumWidth(self.width() - 200 - 10)

        self.status_label = QLabel(f'Downloading from {url}', self)
        self.status_label.move(5, 25)
        self.status_label.setMaximumWidth(self.width() - 200 - 10)

        self.speed_label = QLabel('', self)
        self.speed_label.move(self.progress_bar.pos().x() + 2,
                              self.progress_bar.pos().y() + self.progress_bar.height() + 2)
        self.speed_label.setMaximumWidth(120)

        self.time_label = QLabel('∞', self)
        self.time_label.setMaximumWidth(80)
        self.adjustSize()
        self.time_label.move(self.progress_bar.pos().x() + self.progress_bar.width() - 2 - self.time_label.width(),
                             self.progress_bar.pos().y() + self.progress_bar.height() + 2)

    def average_speed(self, speed):
        speed = parse_filesize(speed[:-2])
        if len(self.speed) > 30:
            self.speed.pop(0)
        self.speed.append(speed)
        average = 0
        for i in self.speed:
            average += i
        return format_bytes(average / len(self.speed)) + '/s'

    def update_progress(self, progress=None, speed=None):
        if progress == 100:
            self.progress_bar.setValue(progress)
            self.speed_label.setText('0.0B/s')
            self.time_label.setText('00:00')
            return

        if progress is not None:
            self.progress_bar.setValue(progress)

        if speed is not None:
            if speed.startswith('Unknown'):
                return
            if str_to_int(speed) == 0.0:
                self.time_label.setText('∞')
                self.speed_label.setText(speed)

            else:
                average_speed = self.average_speed(speed)

                self.speed_label.setText(average_speed)

                if progress is not None and time.time() - self.time > 0.5:
                    ratio = (100 - progress) / 100
                    remaining = parse_filesize(self.size) * ratio / parse_filesize(average_speed)
                    self.time_label.setText(int_to_time(remaining))
                    self.time = time.time()

            self.speed_label.adjustSize()

            self.time_label.adjustSize()
            self.time_label.move(self.progress_bar.pos().x() + self.progress_bar.width() - 2 - self.time_label.width(),
                                 self.progress_bar.pos().y() + self.progress_bar.height() + 2)

    def set_size(self, size):
        self.size = size
        self.progress_bar.setFormat(f'%p% of {size}')

    def update_status(self, status):
        self.status_label.setText(status)

    def update_name(self, name):
        self.download_name.setText(name)
        self.download_name.adjustSize()


def time_to_int(time):
    if time == '∞':
        return float('inf')
    t = time.split(':')
    sec = 0
    for i in range(len(t)):
        sec += int(t[i]) * (60 ** (len(t) - 1 - i))
    return sec


def int_to_time(sec):
    h = int(sec / 3600)
    m = int(sec / 60 - h * 60)
    s = int(sec - m * 60 - h * 3600)
    if h == 0:
        time = f'{m:02}:{s:02}'
    else:
        time = f'{h:02}:{m:02}:{s:02}'
    return time


def str_to_int(string: str):
    return float(re.sub(r'[^0-9.]', "", string))


def str_minus_num(string: str):
    return re.sub(r'\d.', '', string)


app = QApplication(sys.argv)

window = MainWindow()
window.show()

stack = window.stack

ytdl = YTDL(stack)
window.add_view(ytdl)

Directory = View(stack, 'Directory')
window.add_view(Directory)

sys.exit(app.exec())
