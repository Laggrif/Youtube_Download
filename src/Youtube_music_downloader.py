import json
import multiprocessing
import os.path
import subprocess
import time
from multiprocessing import Process
from os.path import sep

import yt_dlp as yt
from mutagen.easyid3 import EasyID3
from PySide6.QtCore import Signal, QObject
from yt_dlp.postprocessor import FFmpegPostProcessor, PostProcessor
from src.Directory import application_path, data_path


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

    def __init__(self, url, path):
        super().__init__(parent=None)
        self.id = self.__hash__()
        self.url = url
        self.path = path
        self.filter = Filter(self, None)

    def download(self):

        ydl_opts = {
            'format': 'bestaudio/best',
            'restrictfilenames': True,
            'outtmpl': self.path + '/%(title)s.%(ext)s',
            """"'ignoreerrors': True,"""
            'match_filter': self.filter.filter,
        }

        if self.sig is not None and self.id is not None:
            ydl_opts['logger'] = Logger(self.sig, self.id)

        with yt.YoutubeDL(ydl_opts) as ydl:
            # yt.utils.POSTPROCESS_WHEN
            ydl.add_post_processor(self.filter["ffmpeg"], when='post_process')
            ydl.add_post_processor(self.filter["metadata"], when='post_process')
            ydl.add_post_processor(self.filter["finished"], when='post_process')
            ydl.download([self.url])

    def run(self):
        self.downloads[self.id] = self
        self.download()

    def stop(self):
        self.filter.stop()
        if self.filter["ffmpeg"] and self.filter["ffmpeg"].proc:
            print("\nstopping ffmpeg process\n")
            self.filter["ffmpeg"].proc.communicate(input='q')
            self.filter["ffmpeg"].proc.wait()
            if not self.filter["ffmpeg"].done and self.filter["ffmpeg"].out and os.path.exists(self.filter["ffmpeg"].out):
                os.remove(self.filter["ffmpeg"].out)
        self.finished.emit()
        del self.downloads[self.id]


class Filter:
    def __init__(self, parent, args):
        self.parent = parent
        self.args = args
        # TODO set up filter from args
        self.filters = {
            "metadata": MetadataPostProcessor(),
            "ffmpeg": FFMpegThreadToMP3(),
            "finished": Finished(signal=self.parent.finished, id=self.parent.id)
        }
        self.filters["metadata"].on = False
        self.filters["ffmpeg"].on = False

    def filter(self, info):
        print("Filter")

    def stop(self):
        for f in self.filters.values():
            f.on = False

    def __getitem__(self, item):
        return self.filters[item]


class Finished(PostProcessor):
    def __init__(self, downloader=None, signal=None, id=None, on=True):
        super().__init__(downloader)
        self.signal = signal
        self.id = id
        self.on = on

    def run(self, info):
        if self.on:
            self.signal.emit()
            del DownloadThread.downloads[self.id]
        return [], info


class FFMpegThreadToMP3(PostProcessor):
    def __init__(self, downloader=None, on=True):
        super().__init__(downloader)
        self.proc = None
        self.out = None
        self.on = on
        self.done = False

    def run(self, information, format='mp3'):
        if self.on:
            input_file = information['filepath']
            self.out = input_file.rsplit('.', 1)[0] + f'.{format}'
            self.to_screen(f'[ffmpeg format]: {format}', prefix=False)
            self.proc = subprocess.Popen(
                f'"{application_path}\\ffmpeg\\bin\\ffmpeg.exe" -y -i "{input_file}" -vn -acodec libmp3lame "{self.out}"',
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE,
                universal_newlines=True)
            for line in self.proc.stderr:
                if line.startswith('size='):
                    self.to_screen('[ffmpeg]: ' + line.replace('\n', ''), prefix=False)
                else:
                    print(line.replace('\n', ''))
            self.proc.wait()
            if self.on:
                os.remove(input_file)
                information['filepath'] = self.out
                self.done = True
        return [], information


class MetadataPostProcessor(PostProcessor):

    def __init__(self, downloader=None, on=True):
        super().__init__(downloader)
        self.on = on

    def run(self, info):
        if self.on:
            id3 = EasyID3(info['filepath'])
            print(id3.keys())
            id3['title'] = info['title']
            id3['artist'] = info['uploader']
            if 'playlist_title' in info:
                id3['album'] = info['playlist_title']
            id3['date'] = info['upload_date']
            if 'playlist_index' in info and info['playlist_index']:
                id3['tracknumber'] = info['playlist_index']
            id3.save()
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
            if data.startswith('size='):
                size_ = data.split('time=', 1)
                time_ = size_[1].split('bitrate=', 1)
                bitrate = time_[1].split('speed=', 1)[0].replace('its', '')
                # format: size, time, bitrate
                self.signal.emit([self.id,
                                  [size_[0],
                                   time_[0],
                                   bitrate,
                                   ]])

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
