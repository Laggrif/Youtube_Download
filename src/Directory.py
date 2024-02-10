import os
import sys

application_path = os.path.dirname(sys.modules['__main__'].__file__)

data_path = os.path.join(os.environ['APPDATA'], 'Youtube Downloader')
