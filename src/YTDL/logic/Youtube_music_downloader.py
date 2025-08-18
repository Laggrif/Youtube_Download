import json
import multiprocessing
import os.path
import subprocess
import time
from multiprocessing import Process
from os.path import sep, join

import yt_dlp as yt
from mutagen.easyid3 import EasyID3
from PySide6.QtCore import Signal, QObject
from yt_dlp.postprocessor import PostProcessor


class DownloadThread(QObject):
    sig = Signal(list)
    downloads = {}
    finished = Signal()

    @staticmethod
    def close_event(event):
        for download in DownloadThread.downloads.copy().values():
            download.stop()
        while len(DownloadThread.downloads) != 0:
            time.sleep(0.5)
        event.accept()

    def __init__(self, url, path, filter):
        super().__init__(parent=None)
        self.id = self.__hash__()
        self.url = url
        self.path = path
        self.filter = filter
        self.filter.init(self)

    def download(self):

        ydl_opts = {
            'format': 'bestaudio/best',
            'restrictfilenames': True,
            'outtmpl': self.path + '/%(title)s.%(ext)s',
            'match_filter': self.filter.filter,
        }

        if self.sig is not None and self.id is not None:
            ydl_opts['logger'] = Logger(self.sig, self.id)

        with yt.YoutubeDL(ydl_opts) as ydl:
            # yt.utils.POSTPROCESS_WHEN
            for p in self.filter.filters.keys():
                if self.filter.filters[p].on and p in self.filter.postprocessors:
                    ydl.add_post_processor(self.filter.filters[p], when='post_process')
            try:
                ydl.download([self.url])
            except Exception as e:
                print("Error in download")
                print(e)

        self.finished.emit()

    def run(self):
        self.downloads[self.id] = self
        self.download()

    def stop(self):
        # stops download but cleans up only if in filtering process
        self.filter.stop()
        if self.filter["ffmpeg"] and self.filter["ffmpeg"].proc:
            self.filter["ffmpeg"].proc.communicate(input='q')
            self.filter["ffmpeg"].proc.wait()
            if not self.filter["ffmpeg"].done and self.filter["ffmpeg"].out and os.path.exists(self.filter["ffmpeg"].out):
                os.remove(self.filter["ffmpeg"].out)
        self.downloads.pop(self.id, None)
        DownloadThread.downloads.pop(self.id, None)


class Filter:
    postprocessors = ["metadata", "ffmpeg"]

    def __init__(self, filters):
        self.parent = None
        self.filters = {**filters}
        print(self.filters["metadata"].data)

    def init(self, parent):
        self.parent = parent

    def filter(self, data):
        pass

    def stop(self):
        for f in self.filters.values():
            f.on = False

    def __getitem__(self, item):
        return self.filters[item]


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

            elif msg.endswith('downloaded'):
                ret = msg.rstrip(" has already been downloaded")
                self.signal.emit([self.id, 'Downloaded: ' + ret.rsplit('\\', 1)[1].rsplit('.', 1)[0]])

            elif msg.startswith('100% of'):
                self.signal.emit([self.id, 'Downloaded size: ' + msg.replace(' ', '').split('of')[1]])

            elif not (msg.startswith('Resuming')):
                _of = msg.replace(' ', '').split('of')
                if 'ETA' in msg:
                    _at = _of[1].replace('~', '').split('at')
                    _in = _at[1].split('ETA')
                    # format: percent, speed, time, size
                    print(_of[0],
                                       _in[0],
                                       _in[1].split('(frag')[0],
                                       _at[0])
                    self.signal.emit([self.id,
                                      [_of[0],
                                       _in[0],
                                       _in[1].split('(frag')[0],
                                       _at[0]
                                       ]
                                      ])

                elif 'in' in msg:
                    _in = _of[1].split('in')
                    _at = _in[1].split('at')
                    print(_of[0],
                                       _at[1],
                                       _at[0],
                                       _in[0].split('(')[0], '---in')
                    self.signal.emit([self.id,
                                      [_of[0],
                                       _at[1],
                                       _at[0],
                                       _in[0].split('(')[0]
                                       ]
                                      ])

                else:
                    self.signal.emit([self.id, 'Already downloaded: ' + msg[1].replace(' ', '')])

        # ffmpeg handling
        elif msg.startswith('[ffmpeg format]'):
            self.signal.emit([self.id, 'ffmpeg format: ' + msg.split(': ', 1)[1]])
        elif msg.startswith('[ffmpeg]'):
            data = msg.split(': ', 1)[1].replace(' ', '')
            if data.startswith('out_time_ms='):
                time_ms = data.split('out_time_ms=', 1)[1]
                self.signal.emit([self.id, 'ffmpeg time: ' + time_ms])
            elif data.startswith('bitrate='):
                self.signal.emit([self.id, 'ffmpeg bitrate: ' + data.replace(' ', '').split('bitrate=', 1)[1]])
            elif data.startswith('Duration:'):
                self.signal.emit([self.id, 'ffmpeg duration: ' + data.split('Duration:', 1)[1].split(',')[0]])

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


if __name__ == "__main__":
    DownloadThread('https://www.youtube.com/watch?v=Jv2uxzhPFl4', '../', 0, None).run()

# lignes de YoutubeDL.py: 375
