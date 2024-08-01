import os
import subprocess
from os.path import join

from yt_dlp.postprocessor import PostProcessor

from src.Directory import application_path


class FFMpegThreadToMP3(PostProcessor):
    ARGS_DICT = {
        "mp3": "-vn -c:a libmp3lame",
        "flac": "-vn -c:a flac",
        **dict.fromkeys(["mp4", "m4a"], "-vn -c:a aac")
    }

    def __init__(self, downloader=None, on=True, format='mp3', codec='', fast=False):
        super().__init__(downloader)
        self.proc = None
        self.out = None
        self.on = on
        self.done = False
        self.format = format
        self.codec = codec
        self.fast = fast

    def run(self, information):
        if self.on:
            input_file = information['filepath']
            self.out = input_file.rsplit('.', 1)[0] + f'.{self.format}'

            if self.fast:
                os.replace(input_file, self.out)
            else:
                self.to_screen(f'[ffmpeg format]: {self.format}', prefix=False)

                if self.format in self.ARGS_DICT.keys() and self.codec == '':
                    args = self.ARGS_DICT[self.format]
                elif self.codec != '':
                    args = f'-codec {self.codec}'
                else:
                    args = '-c copy'

                print(
                    f'"{join(application_path, "ffmpeg", "bin", "ffmpeg.exe")}" -y -i "{input_file}" {args} "{self.out}"')
                self.proc = subprocess.Popen(
                    f'"{join(application_path, "ffmpeg", "bin", "ffmpeg.exe")}" -y -i "{input_file}" {args} "{self.out}"',
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

            if self.on:
                information['filepath'] = self.out
                information['ext'] = self.format
                self.done = True
        return [], information
