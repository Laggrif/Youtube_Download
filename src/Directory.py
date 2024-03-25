import os
import pathlib
import sys

application_path = os.path.dirname(sys.modules['__main__'].__file__)

if os.name == 'nt':
    data_path = os.path.join(os.environ['APPDATA'], 'Youtube Downloader')
elif os.name == 'posix':
    data_path = os.path.join(pathlib.Path.home(), '.Youtube Downloader')
else:
    Exception("Your os is not supported")
