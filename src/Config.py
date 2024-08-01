from PySide6.QtCore import QSettings
from src.Directory import data_path

QSettings.setPath(QSettings.Format.IniFormat, QSettings.Scope.UserScope, data_path + '/config')
QSettings.setDefaultFormat(QSettings.Format.IniFormat)

settings = QSettings(QSettings.Format.IniFormat, QSettings.Scope.UserScope, 'Youtube Downloader')


def default_path():
    return settings.value('default path')


def set_default_path(path):
    settings.setValue('default path', path)


def save_config():
    settings.sync()


def get(key, group=None):
    if type(group) is str:
        value = settings.value(group + "/" + key)
        return value
    elif type(group) is list:
        value = settings.value("/".join(group) + "/" + key)
        return value
    elif group is None:
        return settings.value(key)


def put(key, value, group=None):
    if type(group) is str:
        settings.setValue(group + "/" + key, value)
        return
    elif type(group) is list:
        settings.setValue("/".join(group) + "/" + key, value)
        return
    elif group is None:
        settings.setValue(key, value)


if not settings.contains('default path'):
    set_default_path('C:/')
if not settings.contains('history'):
    put('history', {})
if not settings.contains('save_cookies'):
    put('save_cookies', False)
