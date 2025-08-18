from enum import Enum
from pathlib import Path
from typing import Optional, Any

from PySide6.QtCore import QSettings
from src.Directory import data_path


class SettingSkeleton:
    TYPE_CONVERTERS = {
        bool: (lambda x: x if isinstance(x, bool) else x.lower() == 'true', bool)
    }

    def __init__(self, setting: QSettings, path: str, default=None, tipe: Optional[type] = None):
        self.settings = setting
        self.category = path
        self.tipe = tipe
        if default is not None and not self.settings.contains(self.category):
            self.set(default)

        if self.tipe in self.TYPE_CONVERTERS:
            self._get_converter, self._set_converter = self.TYPE_CONVERTERS[self.tipe]
        else:
            self._get_converter = lambda x: x
            self._set_converter = lambda x: x

    def set(self, value: Any) -> None:
        self.settings.setValue(self.category, value)

    def get(self) -> Any:
        return self._get_converter(self.settings.value(self.category))


class Settings:
    def __init__(self):
        QSettings.setPath(QSettings.Format.IniFormat, QSettings.Scope.UserScope, data_path + '/config')
        QSettings.setDefaultFormat(QSettings.Format.IniFormat)
        self.settings = QSettings(QSettings.Format.IniFormat, QSettings.Scope.UserScope, 'Youtube Downloader')

        self.ytdl = self.YTDLSettings(self.settings)

        self.save_on_exit = SettingSkeleton(self.settings, 'save on exit', True, tipe=bool)

    class YTDLSettings:
        def __init__(self, settings: QSettings):
            self.prefix = 'ytdl/'

            self.minimize_to_tray = SettingSkeleton(settings, self.prefix + 'minimize to tray', False, tipe=bool)

            self.history = SettingSkeleton(settings, self.prefix + 'history', {})
            self.cookies = SettingSkeleton(settings, self.prefix + 'cookies', {})
            self.save_history = SettingSkeleton(settings, self.prefix + 'save history', False, tipe=bool)
            self.save_cookies = SettingSkeleton(settings, self.prefix + 'save cookies', False, tipe=bool)

            self.delete_completed_downloads = SettingSkeleton(settings, self.prefix + 'delete completed downloads',
                                                              False, tipe=bool)
            self.save_path = SettingSkeleton(settings, self.prefix + 'save path', True, tipe=bool)
            self.default_path = SettingSkeleton(settings, self.prefix + 'default path',
                                                (Path.home() / 'Downloads').__str__())

            self.album = SettingSkeleton(settings, self.prefix + 'album')
            self.artist = SettingSkeleton(settings, self.prefix + 'artist')
            self.title = SettingSkeleton(settings, self.prefix + 'title')
            self.track_number = SettingSkeleton(settings, self.prefix + 'track number')
            self.author = SettingSkeleton(settings, self.prefix + 'author')
            self.date = SettingSkeleton(settings, self.prefix + 'date')
            self.genre = SettingSkeleton(settings, self.prefix + 'genre')
            self.language = SettingSkeleton(settings, self.prefix + 'language')
            self.length = SettingSkeleton(settings, self.prefix + 'length')
            self.original_date = SettingSkeleton(settings, self.prefix + 'original date')
            self.performer = SettingSkeleton(settings, self.prefix + 'performer')
            self.release_country = SettingSkeleton(settings, self.prefix + 'release country')

            self.extension = SettingSkeleton(settings, self.prefix + 'extension')
            self.codec = SettingSkeleton(settings, self.prefix + 'codec')
            self.quick_convert = SettingSkeleton(settings, self.prefix + 'quick convert', tipe=bool)

    def save_config(self):
        self.settings.sync()


settings = Settings()
