import os
import sys

application_path = "."
if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable) + "\\_internal"
