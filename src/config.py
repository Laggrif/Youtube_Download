import os.path

from PySide6.QtCore import QSettings

QSettings.setPath(QSettings.Format.IniFormat, QSettings.Scope.UserScope, os.path.dirname(os.path.dirname(__file__)) + '/res/config')
QSettings.setDefaultFormat(QSettings.Format.IniFormat)

settings = QSettings(QSettings.Format.IniFormat, QSettings.Scope.UserScope, 'Laggrif', 'Youtube Download')


def default_path():
    return settings.value('default path')


def set_default_path(path):
    settings.setValue('default path', path)


def save_config():
    settings.sync()


def get(key):
    return settings.value(key)


def put(key, value):
    settings.setValue(key, value)


if not settings.contains('default path'):
    set_default_path('C:/')
if not settings.contains('history'):
    put('history', {})

