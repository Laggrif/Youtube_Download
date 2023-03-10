import time
from datetime import datetime

from PySide6.QtCore import QThread, Qt, QEvent
from PySide6.QtGui import QCloseEvent, QIcon, QResizeEvent, QKeyEvent, QShowEvent, QHideEvent, QFont, QFontDatabase, \
    QRegion, QPalette
from PySide6.QtWebEngineCore import QWebEngineProfile, QWebEngineSettings
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import *
from yt_dlp.utils import parse_filesize, format_bytes

import config
from MainWindow import View, MainWindow
from Youtube_music_downloader import DownloadThread
from config import *
from utils import *


class YTDL(View):
    def __init__(self, parent, main_window: MainWindow):
        super().__init__(parent, 'Youtube Download')
        self.main_window = main_window
        self.downloads = {}

        # Dimensions of main window
        self.WIDTH = parent.width()
        self.HEIGHT = parent.height()

        self.browser = YoutubeBrowser(self)

        # Input for url and its label
        self.download_input = QLineEdit(self)
        self.download_input.setObjectName('download_input')
        self.download_input.returnPressed.connect(self.download)
        self.download_input_label = QLabel('Input a youtube url', self)
        self.download_input_label.setObjectName('input_label')
        self.download_input_label.adjustSize()
        self.download_input_label.setGeometry(40 + 5, 80 - 20, self.download_input_label.width(), 20)
        # Button to clear url input
        self.clear_button = QPushButton('', self)
        close_icon = self.style().standardIcon(QStyle.SP_TitleBarCloseButton)
        self.clear_button.setIcon(close_icon)
        self.clear_button.setObjectName('clear_button')
        self.clear_button.clicked.connect(self.clear)

        # Input for path and its label
        self.path_input = QLineEdit(self)
        self.path_input.setText(default_path())
        self.path_input_label = QLabel('Output path', self)
        self.path_input_label.setObjectName('input_label')
        self.path_input_label.adjustSize()
        self.path_input_label.setGeometry(60 + 5, 140 - 20, self.path_input_label.width(), 20)
        # Button to browse file explorer
        self.path_button = QPushButton('Browse', self)
        self.path_button.setObjectName('path_button')
        self.path_button.resize(70, 24)
        self.path_button.clicked.connect(self.file_explorer)

        # Button to download inserted url
        self.download_button = QPushButton('Download', self)
        self.download_button.clicked.connect(self.download)

        self.web_button = QPushButton('Open Browser', self)
        self.web_button.clicked.connect(self.web_browser)

        # Layout for output
        self.output_vbox = QVBoxLayout(self)
        self.output_vbox.setAlignment(Qt.AlignmentFlag.AlignTop)
        # Widget containing output
        self.output_widget = QWidget(self)
        self.output_widget.setLayout(self.output_vbox)
        self.output_widget.setStyleSheet("background-color : grey;")
        # Scroll manager for output
        self.output_scroll = QScrollArea(self)
        self.output_scroll.setWidgetResizable(True)
        self.output_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.output_scroll.setWidget(self.output_widget)

        self.show()

    def clear(self):
        self.download_input.setText('')

    def file_explorer(self):
        path = QFileDialog.getExistingDirectory(None,
                                                'Select a folder',
                                                self.path_input.text(),
                                                QFileDialog.ShowDirsOnly)
        if path != '':
            self.path_input.setText(path)
            set_default_path(path)

    def web_browser(self):
        self.browser.show()

    def download(self, url=None):
        if not url and check_url(self.download_input.text()):
            url = self.download_input.text()
        elif not url:
            return
        th = QThread(None)
        worker = DownloadThread(url, self.path_input.text())
        worker.moveToThread(th)
        th.worker = worker
        th.started.connect(worker.run)
        worker.finished.connect(th.quit())
        worker.sig.connect(self.process_signal)

        self.downloads[worker.__hash__()] = [th, self.add_download_widget()]
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

            elif signal.startswith('Extracting playlist'):
                self.downloads[id].append(signal.split(': ')[1])
                widget.update_status('Downloading playlist from ' + signal.split(': ')[1])

            elif signal.startswith('Playlist name'):
                sig = signal.split(': ', 1)[1]
                if sig == '':
                    widget.update_name('Fetching video name...')
                    widget.update_status('Downloading playlist from ' + self.downloads[id][2])
                else:
                    widget.update_name(sig)

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

    def resizeEvent(self, event: QResizeEvent):
        self.WIDTH = self.main_window.width()
        self.HEIGHT = self.main_window.height()

        for widget in self.output_scroll.children():
            widget.resize(self.WIDTH - 40, widget.height())
        # TODO update sizes based on window size
        event.accept()
        self.show()

    def show(self):
        super().show()
        self.main_window.setMinimumWidth(400)
        self.main_window.setMinimumHeight(320)

        self.resize(self.main_window.size())

        self.path_input.setGeometry(60, 140, self.WIDTH - 120 - 80, 24)
        self.path_button.move(self.path_input.pos().x() + self.path_input.width() + 5,
                              self.path_input.pos().y())

        self.download_input.setGeometry(40, 80, self.WIDTH - 80 - 24, 24)
        self.clear_button.setGeometry(self.download_input.pos().x() + self.download_input.width(),
                                      self.download_input.pos().y(),
                                      24,
                                      24)

        space = max(min(130, int(self.WIDTH / 2 - 100 - 100)), 10)
        self.download_button.setGeometry(int(self.WIDTH / 2 - 100 - space / 2), 200, 100, 30)
        self.web_button.setGeometry(int(self.WIDTH / 2 + space / 2), 200, 100, 30)

        self.output_scroll.setGeometry(0, 250, self.WIDTH, self.HEIGHT - 250)


#    left_space   100    space    width/2

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

        self.download_name = QLabel('Fetching video name...', self)
        self.download_name.move(5, 5)

        self.status_label = QLabel(f'Downloading from {url}', self)
        self.status_label.move(5, 25)

        self.speed_label = QLabel('', self)

        self.time_label = QLabel('∞', self)

        self.show()

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
        self.status_label.adjustSize()

    def update_name(self, name):
        self.download_name.setText(name)
        self.download_name.adjustSize()

    def resizeEvent(self, event: QResizeEvent):
        event.accept()
        self.show()

    def show(self):
        super().show()
        self.progress_bar.setGeometry(int(self.width() / 2) + 10, 5, int(self.width() / 2) - 30, 20)

        self.download_name.setMaximumWidth(int(self.width() / 2) - 10)
        self.download_name.adjustSize()

        self.status_label.setMaximumWidth(int(self.width() / 2) - 10)
        self.status_label.adjustSize()

        self.speed_label.setMaximumWidth(int(self.progress_bar.width() * 0.7) - 2)
        self.speed_label.adjustSize()
        self.speed_label.move(self.progress_bar.pos().x() + 2,
                              self.progress_bar.pos().y() + self.progress_bar.height() + 2)

        self.time_label.setMaximumWidth(int(self.progress_bar.width() * 0.3) - 2)
        self.time_label.adjustSize()
        self.time_label.move(self.progress_bar.pos().x() + self.progress_bar.width() - 2 - self.time_label.width(),
                             self.progress_bar.pos().y() + self.progress_bar.height() + 2)


class YoutubeBrowser(QFrame):
    def __init__(self, parent: YTDL):
        super().__init__()
        self.side_grips = []
        self.corner_grips = []
        self.YTDL = parent
        main_window = parent.parent().parent()
        self.setGeometry(main_window.x() + 40,
                         main_window.y() + 40,
                         main_window.width(),
                         main_window.height() + 30)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setObjectName('youtube_browser')

        self.nav_bar = CustomTitleBar(self)

        self.browser = QWebEngineView(self)
        self.browser.settings().setAttribute(QWebEngineSettings.FullScreenSupportEnabled, True)
        self.browser.page().fullScreenRequested.connect(self.fullscreen_on)

        profile = self.browser.page().profile()
        profile.setPersistentCookiesPolicy(QWebEngineProfile.ForcePersistentCookies)
        profile.setPersistentCookiesPolicy(QWebEngineProfile.NoPersistentCookies)
        self.browser.setUrl('https://www.youtube.com')
        self.browser.urlChanged.connect(self.process_url)

        self.button = QPushButton(self)
        self.button.setGeometry(self.width() - 40, self.height() - 40, 35, 35)
        self.button.setObjectName('download_icon')
        self.button.clicked.connect(self.download)

        self.add_grip()
        self.update_grip()

    def fullscreen_on(self, request):
        if self.isFullScreen():
            self.showNormal()
            self.button.show()
        else:
            self.showFullScreen()
            self.button.hide()
        request.accept()

    def download(self):
        if check_url(self.browser.url().toString()):
            self.YTDL.download(url=self.browser.url().toString())

    def process_url(self):
        if check_url(self.browser.url().toString()):
            self.button.show()
        else:
            self.button.hide()
        self.add_to_history()
        self.nav_bar.change_url(self.browser.url().toString())

    def add_to_history(self):
        history = config.get('history')
        history[self.browser.url()] = datetime.now().strftime('%d%m%Y. %H:%M:%S')
        config.put('history', history)
        config.save_config()

    def back(self):
        self.browser.back()

    def forward(self):
        self.browser.forward()

    def reload(self):
        self.browser.reload()

    def search(self, url):
        self.browser.setUrl(url)

    def add_grip(self):
        gl = SizeGrip(self, Qt.Edge.LeftEdge)
        gt = SizeGrip(self, Qt.Edge.TopEdge)
        gr = SizeGrip(self, Qt.Edge.RightEdge)
        gb = SizeGrip(self, Qt.Edge.BottomEdge)
        self.side_grips = [gt, gr, gb, gl]

        self.corner_grips = [QSizeGrip(self) for i in range(4)]

    def update_grip(self):
        self.side_grips[0].setGeometry(5, 0, self.width() - 10, 5)
        self.side_grips[1].setGeometry(self.width() - 5, 0, 5, self.height() - 10)
        self.side_grips[2].setGeometry(0, self.height() - 5, self.width() - 10, 5)
        self.side_grips[3].setGeometry(0, 5, 5, self.height() - 10)

        self.corner_grips[0].setGeometry(0, 0, 5, 5)
        self.corner_grips[1].setGeometry(self.width() - 5, 0, 5, 5)
        self.corner_grips[2].setGeometry(self.width() - 5, self.height() - 5, 5, 5)
        self.corner_grips[3].setGeometry(0, self.height() - 5, 5, 5)

    def resizeEvent(self, event: QResizeEvent):
        self.show()
        self.update_grip()
        event.accept()

    def show(self) -> None:
        super().show()
        self.nav_bar.setGeometry(0, 0, self.width(), 32)
        self.button.move(self.width() - 40, self.height() - 40)
        self.browser.setGeometry(0, 32, self.width(), self.height() - 32)


class CustomTitleBar(QFrame):
    clickPos = None

    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName('custom_title_bar')

        self.close_button = QPushButton('⛌', self)
        self.close_button.setObjectName('windows_close_button')
        self.close_button.clicked.connect(self.parent().close)

        self.maximize_button = QPushButton('⃞', self)
        self.maximize_button.setObjectName('windows_maximize_button')
        self.maximize_button.clicked.connect(self.maximize)

        self.forward_button = QPushButton('🡪', self)
        self.forward_button.setFont(QFont('Arial', 12))
        self.forward_button.setGeometry(45, 1, 30, 28)
        self.forward_button.setObjectName('web_navigation_button')
        self.forward_button.clicked.connect(self.parent().forward)

        self.back_button = QPushButton('🡨', self)
        self.back_button.setFont(QFont('Arial', 12))
        self.back_button.setGeometry(20, 1, 30, 28)
        self.back_button.setObjectName('web_navigation_button')
        self.back_button.clicked.connect(self.parent().back)

        self.reload_button = QPushButton('⭮', self)
        self.reload_button.setFont(QFont('Arial', 15))
        self.reload_button.setGeometry(90, 1, 30, 28)
        self.reload_button.setObjectName('web_navigation_button')
        self.reload_button.clicked.connect(self.parent().reload)

        self.search_bar = QLineEdit(self)
        self.search_bar.setObjectName('download_input')
        self.search_bar.setFont(QFont('Arial', 15))
        self.search_bar.returnPressed.connect(self.search)

        self.search_button = QPushButton(self)
        self.search_button.setIcon(QIcon('./res/icon/search.png'))
        self.search_button.setObjectName('search_button')
        self.search_button.clicked.connect(self.search)

    def change_url(self, url):
        self.search_bar.setText(url)

    def search(self):
        self.parent().search(self.search_bar.text())

    def maximize(self):
        if self.parent().isMaximized():
            self.maximize_button.setText('⃞')
            self.parent().showNormal()
        else:
            self.maximize_button.setText('❐')
            self.parent().showMaximized()

    def resizeEvent(self, event: QResizeEvent):
        self.show()
        event.accept()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clickPos = event.scenePosition().toPoint()

    def mouseMoveEvent(self, event):
        if self.clickPos is not None:
            self.window().move(event.globalPosition().toPoint() - self.clickPos)

    def mouseReleaseEvent(self, QMouseEvent):
        self.clickPos = None

    def closeClicked(self):
        self.window().close()

    def maxClicked(self):
        self.window().showMaximized()

    def normalClicked(self):
        self.window().showNormal()

    def minClicked(self):
        self.window().showMinimized()

    def show(self) -> None:
        self.close_button.setGeometry(self.width() - 45, 0, 45, 30)
        self.maximize_button.setGeometry(self.width() - 90, 0, 45, 30)
        self.search_bar.setGeometry(self.width() / 4, 3, self.width() / 2 - 24, 24)
        self.search_button.setGeometry(self.width() / 4 * 3 - 24, 3, 24, 24)


class SizeGrip(QWidget):
    def __init__(self, parent, edge):
        QWidget.__init__(self, parent)
        if edge == Qt.LeftEdge:
            self.setCursor(Qt.SizeHorCursor)
            self.resizeFunc = self.resizeLeft
        elif edge == Qt.TopEdge:
            self.setCursor(Qt.SizeVerCursor)
            self.resizeFunc = self.resizeTop
        elif edge == Qt.RightEdge:
            self.setCursor(Qt.SizeHorCursor)
            self.resizeFunc = self.resizeRight
        else:
            self.setCursor(Qt.SizeVerCursor)
            self.resizeFunc = self.resizeBottom
        self.mousePos = None

    def resizeLeft(self, delta):
        window = self.window()
        width = max(window.minimumWidth(), window.width() - delta.x())
        geo = window.geometry()
        geo.setLeft(geo.right() - width)
        window.setGeometry(geo)

    def resizeTop(self, delta):
        window = self.window()
        height = max(window.minimumHeight(), window.height() - delta.y())
        geo = window.geometry()
        geo.setTop(geo.bottom() - height)
        window.setGeometry(geo)

    def resizeRight(self, delta):
        window = self.window()
        width = max(window.minimumWidth(), window.width() + delta.x())
        window.resize(width, window.height())

    def resizeBottom(self, delta):
        window = self.window()
        height = max(window.minimumHeight(), window.height() + delta.y())
        window.resize(window.width(), height)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.mousePos = event.pos()

    def mouseMoveEvent(self, event):
        if self.mousePos is not None:
            delta = event.pos() - self.mousePos
            self.resizeFunc(delta)

    def mouseReleaseEvent(self, event):
        self.mousePos = None
