import time
from datetime import datetime

from PySide6.QtCore import QThread, Qt
from PySide6.QtGui import QCloseEvent, QIcon, QResizeEvent
from PySide6.QtWebEngineCore import QWebEngineProfile, QWebEngineSettings
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import *
from yt_dlp.utils import parse_filesize, format_bytes

import config
from MainWindow import View
from Youtube_music_downloader import DownloadThread
from config import *
from utils import *


class YTDL(View):
    def __init__(self, parent):
        super().__init__(parent, 'Youtube Download')
        self.downloads = {}

        # Dimensions of main window
        self.WIDTH = parent.width()
        self.HEIGHT = parent.height()

        self.browser = YoutubeBrowser(self)

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
        self.path_input.setText(default_path())
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
        self.browser.show()

    def file_explorer(self):
        path = QFileDialog.getExistingDirectory(None,
                                                'Select a folder',
                                                self.path_input.text(),
                                                QFileDialog.ShowDirsOnly)
        if path != '':
            self.path_input.setText(path)
            set_default_path(path)

    def download(self, url=None):
        print(url)
        if url is None and self.download_input.text() != '':
            url = self.download_input.text()
        elif url is None:
            return
        th = QThread(None)
        worker = DownloadThread(url, self.path_input.text(), len(self.downloads))
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
            if signal.startswith(('Delete', 'error')):
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


class YoutubeBrowser(QWebEngineView):
    banned_urls = ['https://www.youtube.com/feed/subscriptions',
                   'https://www.youtube.com/feed/library',
                   'https://www.youtube.com/feed/history',
                   'https://www.youtube.com/reporthistory',
                   'https://www.youtube.com'
                   ]
    banned_url_content = [
        '/signin',
        'https://www.youtube.com/feed/',
        'https://www.youtube.com/account',
        'https://www.youtube.com/channel',
        'https://www.youtube.com/gaming',
        'https://www.youtube.com/premium'
    ]

    def __init__(self, parent: YTDL):
        super().__init__()
        self.YTDL = parent

        main_window = parent.parent().parent()

        self.setGeometry(main_window.x() + int(main_window.width() / 2) - 250, main_window.y(), 500, 700)

        # support fullscreen videos
        self.settings().setAttribute(QWebEngineSettings.FullScreenSupportEnabled, True)
        self.page().fullScreenRequested.connect(self.fullscreen_on)

        profile = self.page().profile()
        profile.setCachePath('cache')
        profile.setPersistentStoragePath('persistent_storage')
        profile.setPersistentCookiesPolicy(QWebEngineProfile.ForcePersistentCookies)
        profile.setPersistentCookiesPolicy(QWebEngineProfile.NoPersistentCookies)
        self.setUrl('https://www.youtube.com')
        self.urlChanged.connect(self.process_url)

        self.button = QPushButton(self)
        self.button.setGeometry(self.width() - 40, self.height() - 40, 35, 35)
        self.button.setObjectName('download_icon')
        self.button.clicked.connect(self.download)

    def fullscreen_on(self, request):
        if self.isFullScreen():
            self.showNormal()
            self.button.show()
        else:
            self.showFullScreen()
            self.button.hide()
        request.accept()

    def download(self):
        if self.check_url():
            self.YTDL.download(url=self.url().toString())

    def process_url(self):
        if self.check_url():
            self.button.show()
        else:
            self.button.hide()
        self.add_to_history()

    def add_to_history(self):
        history = config.get('history')
        history[self.url()] = datetime.now().strftime('%d%m%Y. %H:%M:%S')
        config.put('history', history)
        config.save_config()

    def closeEvent(self, event: QCloseEvent):
        self.hide()
        event.accept()

    def resizeEvent(self, event: QResizeEvent):
        self.button.move(self.width() - 40, self.height() - 40)
        event.accept()

    def check_url(self):
        url = self.url().toString()
        for i in self.banned_url_content:
            if url.__contains__(i):
                return False
        for i in self.banned_urls:
            if url == i or url == i + '/':
                return False
        return True
