import os.path
import time
from os.path import join

from PySide6.QtCore import QThread, Qt, QPoint, QPropertyAnimation, QEasingCurve, \
    QParallelAnimationGroup, QSize, QObject, QEvent, QAbstractAnimation
from PySide6.QtGui import QIcon, QResizeEvent, QPainter, QColor
from PySide6.QtWidgets import *
from yt_dlp.utils import parse_filesize, format_bytes

from src.MainWindow import View, MainWindow
from src.YTDL.Browser import YoutubeBrowser
from src.YTDL.SideBar import SideBar
from src.YTDL.logic.Youtube_music_downloader import DownloadThread, Filter
from src.Config import *
from src.utils import *
from src.Directory import application_path
from src.StyleSheetParser import get_style


def work(foo):
    foo.run()


class Leaver:
    def __init__(self, id, parent):
        self.id = id
        self.parent = parent

    def leave(self):
        self.parent.downloads[self.id][0].quit()
        self.parent.downloads[self.id][0].wait()
        self.parent.downloads[self.id][1].deleteLater()
        del self.parent.downloads[self.id]


class YTDL(View):
    def __init__(self, parent, main_window: MainWindow):
        super().__init__(parent, 'Youtube Download')
        self.config_category = ['YT_Settings']
        self.setStyleSheet(get_style())
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
        self.path_input.setObjectName('path_input')
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

        # ------------------ Sidebar ------------------
        self.sidebar_open = False
        # opaque background for sidebar

        class Darken(QWidget):
            def mouseReleaseEvent(self, event):
                if self.parent().darken_anim.state() != QAbstractAnimation.State.Running:
                    self.parent().toggle_side_bar()
        self.darken = Darken(self)
        self.darken.setAttribute(Qt.WA_StyledBackground, True)
        self.darken.setObjectName('darken')
        self.darken.setStyleSheet("background-color: #000000;")
        self.darken.setGeometry(0, 0, self.WIDTH, self.HEIGHT)

        # sidebar
        self.sideBar = SideBar(self)
        self.sideBar.setGeometry(self.WIDTH, 0, self.WIDTH - 100, self.height())
        self.sideBar.setFixedWidth(self.WIDTH - 100)
        # sidebar button
        self.settings_button = QPushButton(parent=self)
        self.settings_button.setIcon(QIcon(os.path.join(application_path, 'res', 'icon', 'settings.png')))
        self.settings_button.setIconSize(QSize(16, 16))
        self.settings_button.setStyleSheet('border-radius: 0; margin: 0; padding: 0;')
        self.settings_button.setObjectName('settings_button')
        self.settings_button.setGeometry(self.WIDTH - 22, 0, 22, 22)
        self.settings_button.clicked.connect(self.toggle_side_bar)
        self.settings_button.show()
        # animations
        effect = QGraphicsOpacityEffect(self.darken)
        effect.setOpacity(0)
        animationduration = 200
        self.darken.setGraphicsEffect(effect)
        self.darken_anim = QPropertyAnimation(effect, b'opacity')
        self.darken_anim.setDuration(animationduration)
        self.darken_anim.setEasingCurve(QEasingCurve.InOutCubic)
        self.darken_anim.finished.connect(lambda: self.darken.move(0 if self.sidebar_open else self.WIDTH, 0))
        self.sideBar_anim = QPropertyAnimation(self.sideBar, b'pos')
        self.sideBar_anim.setDuration(animationduration)
        self.sideBar_anim.setEasingCurve(QEasingCurve.InOutCubic)
        self.settings_button_anim = QPropertyAnimation(self.settings_button, b'pos')
        self.settings_button_anim.setDuration(animationduration)
        self.settings_button_anim.setEasingCurve(QEasingCurve.InOutCubic)
        self.anims = QParallelAnimationGroup()
        self.anims.addAnimation(self.darken_anim)
        self.anims.addAnimation(self.sideBar_anim)
        self.anims.addAnimation(self.settings_button_anim)

        self.show()

    def toggle_side_bar(self):
        self.anims.stop()
        if not self.sidebar_open:
            self.sidebar_open = True
            self.darken.move(0, 0)
            self.settings_button_anim.setEndValue(QPoint(self.WIDTH - 20 - self.sideBar.width(), 0))
            self.sideBar_anim.setEndValue(QPoint(self.WIDTH - self.sideBar.width(), 0))
            self.darken_anim.setEndValue(0.5)
            self.anims.start()
        else:
            self.sidebar_open = False
            self.settings_button_anim.setEndValue(QPoint(self.WIDTH - 20, 0))
            self.sideBar_anim.setEndValue(QPoint(self.WIDTH, 0))
            self.darken_anim.setEndValue(0)
            self.anims.start()

    def show_side_bar(self):
        if self.sidebar_open:
            self.sideBar.setGeometry(100, 0, self.WIDTH - 100, self.height())
            self.settings_button.setGeometry(self.WIDTH - 20 - self.sideBar.width(), 0, 20, 20)
        else:
            self.sideBar.setGeometry(self.WIDTH, 0, self.WIDTH - 100, self.height())
            self.settings_button.setGeometry(self.WIDTH - 20, 0, 20, 20)
        self.darken.setGeometry(0 if self.sidebar_open else self.WIDTH, 0, self.WIDTH, self.HEIGHT)

    def clear(self):
        self.download_input.setText('')

    def file_explorer(self):
        path = QFileDialog.getExistingDirectory(None,
                                                'Select a folder',
                                                self.path_input.text(),
                                                QFileDialog.ShowDirsOnly)
        if path != '':
            self.path_input.setText(path)

    def web_browser(self):
        self.browser.show()

    def build_filter(self):
        # widgets must handle by themselves if the processor must be on or off
        filters = {
            "ffmpeg": self.sideBar.ffmpeg.get_processor(),
            "metadata": self.sideBar.metadata.get_processor(),
        }
        return Filter(filters)

    def download(self, url=None):
        filter = self.build_filter()

        if not url and check_url(self.download_input.text()):
            url = self.download_input.text()
        elif not url:
            return
        th = QThread(None)
        worker = DownloadThread(url, self.path_input.text(), filter)
        worker.moveToThread(th)
        th.worker = worker
        th.started.connect(worker.run)
        id = worker.__hash__()
        self.downloads[id] = [th, self.add_download_widget(), worker]
        leaver = Leaver(id, self)
        worker.finished.connect(lambda: leaver.leave())
        worker.sig.connect(self.process_signal)
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
                pass
                """
                self.downloads[id][0].quit()
                self.downloads[id][0].wait()
                widget.deleteLater()
                del self.downloads[id]
                """

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

            elif signal.startswith('Downloaded size'):
                print(signal.split(': ')[1])
                widget.update_progress(100)
                widget.set_size(signal.split(': ')[1])

            elif signal.startswith('Downloaded'):
                widget.update_progress(100)
                widget.update_name(signal.split(': ')[1])
                widget.update_status('Already downloaded')

        elif isinstance(signal, list):
            print(signal)
            if len(signal) == 4:
                widget.set_size(signal[3])
                widget.update_progress(float(signal[0].replace('%', '')), signal[1])

            if len(signal) == 3:
                if signal[0] == 'size':
                    print('size')
                    widget.set_size(signal[1])
                widget.update_progress(1.0, signal[2])


        self.output_scroll.update()

    def add_download_widget(self):
        widget = ProgressWidget(self.output_widget, self.output_vbox, len(self.downloads), self.download_input.text())

        return widget

    def resizeEvent(self, event: QResizeEvent):
        self.WIDTH = self.main_window.width()
        self.HEIGHT = self.main_window.height()

        for widget in self.output_scroll.children():
            widget.resize(self.WIDTH - 40, widget.height())

        self.sideBar.setGeometry(self.WIDTH - self.sideBar.width(), 0, self.sideBar.width(), self.HEIGHT)

        self.show_side_bar()
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

        self.show_side_bar()

    def closeEvent(self, event):
        self.sideBar.save_config()
        if get("save_download_path", self.config_category) == "true":
            print(self.path_input.text())
            set_default_path(self.path_input.text())
        save_config()
        if len(self.downloads) != 0:
            quit_msg = ("Are you sure you want to exit the program? \nAll downloads will be stopped: "
                        "incomplete downloads will be deleted.")
            reply = QMessageBox.question(self, 'Confirm Exit', quit_msg, QMessageBox.Yes, QMessageBox.No)

            if reply == QMessageBox.Yes:
                DownloadThread.close_event(event)
            else:
                event.ignore()
        elif self.isVisible():
            event.accept()


#    left_space   100    space    width/2

class ProgressWidget(QFrame):
    def __init__(self, output_widget, output_vbox, pos, url):
        super().__init__(output_widget)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setObjectName('ProgressWidget')
        self.setStyleSheet(get_style())

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
                self.speed_label.setText('-B/s')
                self.time_label.setText('∞')
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

