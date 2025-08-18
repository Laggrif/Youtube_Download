from datetime import datetime
from os.path import join

from PySide6.QtCore import Qt, QDateTime
from PySide6.QtGui import QFont, QIcon, QResizeEvent
from PySide6.QtNetwork import QNetworkCookie
from PySide6.QtWebEngineCore import QWebEngineProfile, QWebEnginePage
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QFrame, QPushButton, QLineEdit, QWidget, QSizeGrip

from src.Config import settings
from src.Directory import application_path
from src.StyleSheetParser import get_style
from src.utils import check_url


# TODO aesthetic changes must be made
class YoutubeBrowser(QFrame):
    save_cookies = False
    save_history = False

    def __init__(self, parent):
        super().__init__()
        self.save_cookies = settings.ytdl.save_cookies.get()
        self.save_history = settings.ytdl.save_history.get()
        self.cookies = []
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

        self.setStyleSheet(get_style())

        self.nav_bar = CustomTitleBar(self)

        self.browser = QWebEngineView(self)
        self.browser.page().fullScreenRequested.connect(self.fullscreen_on)

        self.profile_browser = QWebEngineProfile.defaultProfile()
        self.page_browser = QWebEnginePage(self.profile_browser, self.browser)
        self.browser.setPage(self.page_browser)
        self.cookie_store = self.profile_browser.cookieStore()

        self.cookie_store.cookieAdded.connect(lambda cook: self.cookies.append(cook))
        self.load_session()

        self.browser.setUrl('https://www.youtube.com')
        self.browser.urlChanged.connect(self.process_url)

        self.button = QPushButton(self)
        self.button.setGeometry(self.width() - 40, self.height() - 40, 35, 35)
        self.button.setObjectName('download_icon')
        self.button.clicked.connect(self.download)

        self.add_grip()
        self.update_grip()

    def save_session(self):
        if self.save_cookies:
            serializable_cookies = {}
            for cookie in self.cookies:
                cook = {
                    'name': cookie.name(),
                    'value': cookie.value(),
                    'domain': cookie.domain(),
                    'path': cookie.path(),
                    'secure': cookie.isSecure(),
                    'httpOnly': cookie.isHttpOnly(),
                    'expirationDate': cookie.expirationDate().toSecsSinceEpoch()
                }
                serializable_cookies[cookie.name()] = cook
            settings.ytdl.cookies.set(serializable_cookies)

    def load_session(self):
        # TODO Might be a huge security risk
        cookies = settings.ytdl.cookies.get()
        if not cookies:
            return
        self.cookie_store.deleteAllCookies()
        for cookie in cookies.values():
            if QDateTime.currentSecsSinceEpoch() > cookie['expirationDate'] >= 0:
                continue
            cook = QNetworkCookie()
            cook.setName(cookie['name'])
            cook.setValue(cookie['value'])
            cook.setDomain(cookie['domain'])
            cook.setPath(cookie['path'])
            cook.setSecure(cookie['secure'])
            cook.setHttpOnly(cookie['httpOnly'])
            cook.setExpirationDate(QDateTime.fromSecsSinceEpoch(cookie['expirationDate']))

            self.cookie_store.setCookie(cook)

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
        if self.save_history:
            self.add_to_history()
        self.nav_bar.change_url(self.browser.url().toString())

    def add_to_history(self):
        history = settings.ytdl.history.get()
        history[self.browser.url()] = datetime.now().strftime('%d%m%Y. %H:%M:%S')
        settings.ytdl.history.set(history)
        settings.save_config()

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
        self.search_button.setIcon(QIcon(join(application_path, 'res', 'icon', 'search.png')))
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
        self.close_button.setGeometry(self.width() - 45, 1, 45, 30)
        self.maximize_button.setGeometry(self.width() - 90, 1, 45, 30)
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

