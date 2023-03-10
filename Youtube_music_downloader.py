import json
import os.path
from os.path import sep
from pathlib import Path

import yt_dlp as yt
from PySide6.QtCore import Signal, QObject
from yt_dlp.postprocessor import FFmpegPostProcessor, PostProcessor


class DownloadThread(QObject):
    sig = Signal(list)
    finished = Signal()

    def __init__(self, url, path):
        super().__init__(parent=None)
        self.id = self.__hash__()
        self.url = url
        self.path = path

    def download(self):
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'restrictfilenames': True,
            'outtmpl': self.path + '/%(title)s.%(ext)s',
        }

        if self.sig is not None and self.id is not None:
            ydl_opts['logger'] = Logger(self.sig, self.id)

        with yt.YoutubeDL(ydl_opts) as ydl:
            ydl.add_post_processor(MetadataPostProcessor(), when='post_process')
            ydl.download([self.url])

    def run(self):
        self.download()
        self.finished.emit()


class MetadataPostProcessor(PostProcessor):
    def run(self, info):
        with open('data', 'w') as fp:
            json.dump(info, fp, indent=4)
        return [], info


class Logger:
    def __init__(self, signal: Signal, id):
        self.signal = signal
        self.id = id
        self.is_playlist = False

    def debug(self, msg):
        if msg.startswith('[debug] ') or msg.startswith('[MetadataPostProcess]'):
            pass
        else:
            self.info(msg)

    def info(self, msg: str):
        print(msg)
        # [youtube] handling
        if msg.startswith('[youtube] Extracting URL'):
            self.signal.emit([self.id, 'Extracting:' + msg.split(':', 1)[1]])
        elif msg.startswith('[youtube]'):
            pass

        elif msg.startswith('[youtube:tab] Extracting'):
            self.is_playlist = True
            self.signal.emit([self.id, 'Extracting playlist:' + msg.split(':', 1)[1]])

        # [info] handling
        elif msg.startswith('[info]'):
            pass

        # [download] handling
        elif msg.startswith('[download]'):
            msg = msg.lstrip('[download] ')
            # playlist handling
            if msg.startswith('Downloading item'):
                msg = msg.lstrip('Downloading item ').split(' of ')
                self.signal.emit([self.id, 'Playlist name: '])
            elif msg.startswith('Downloading playlist'):
                self.signal.emit([self.id, 'Playlist name:' + msg.split(':')[1]])
            elif msg.startswith('Finished'):
                self.signal.emit([self.id, 'Delete'])

            # video handling
            elif msg.startswith('Destination'):
                msg = msg.rsplit('.', 1)[0].rsplit(sep, 1)[1]
                self.signal.emit([self.id, 'Name: ' + msg])
            elif not (msg.startswith('Resuming') or msg.endswith('downloaded')):
                _of = msg.split('of ')
                if 'ETA' in msg:
                    _at = _of[1].rstrip('~').split('at ')
                    _in = _at[1].split('ETA ')
                    # format: percent, speed, time, size
                    self.signal.emit([self.id,
                                      [_of[0].replace(' ', ''),
                                       _in[0].replace(' ', ''),
                                       _in[1].replace(' ', ''),
                                       _at[0].replace(' ', '')
                                       ]
                                      ])

                elif 'in' in msg:
                    _in = _of[1].split('in ')
                    _at = _in[1].split('at ')
                    self.signal.emit([self.id,
                                      [_of[0].replace(' ', ''),
                                       _at[1].replace(' ', ''),
                                       _at[0].replace(' ', ''),
                                       _in[0].replace(' ', '')
                                       ]
                                      ])

                else:
                    self.signal.emit([self.id, 'Already downloaded: ' + _of[1].replace(' ', '')])

        # [ExtractAudio] handling
        elif msg.startswith('[ExtractAudio]'):
            msg = msg.rsplit(sep, 1)[1]
            self.signal.emit([self.id, 'Destination: ' + msg])

        # Deleting handling
        elif msg.startswith('Deleting') and not self.is_playlist:
            self.signal.emit([self.id, 'Delete'])

        # other case
        else:
            self.signal.emit([self.id, msg, 'else'])

    def warning(self, msg):
        self.signal.emit([self.id, 'warning'])

    def error(self, msg):
        self.signal.emit([self.id, 'error'])


class ffmpeg_location:
    def get(self):
        return os.path.dirname(__file__) + '/ffmpeg/bin'


FFmpegPostProcessor._ffmpeg_location = ffmpeg_location()


if __name__ == "__main__":
    DownloadThread('https://www.youtube.com/watch?v=Jv2uxzhPFl4', './', 0, None).run()

# lignes de YoutubeDL.py: 375
