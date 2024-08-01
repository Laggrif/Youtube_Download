import json
import subprocess
from os.path import join

import mutagen
from mutagen.apev2 import APEv2
from mutagen.easyid3 import EasyID3
from mutagen.easymp4 import EasyMP4
from mutagen.flac import FLAC
from mutagen.mp4 import MP4
from yt_dlp.postprocessor import PostProcessor

from src.Directory import application_path
from src.YTDL.logic.string_parser import Parser

IMPORTANT_METADATA = [
    'album',
    'artist',
    'author',
    'date',
    'genre',
    'language',
    'length',
    'originaldate',
    'performer',
    'releasecountry',
    'title',
    'tracknumber'
]

equivalent = {
    "album": "album",
    "artist": "artist",
    "author": "composer",
    "date": "date",
    "genre": "genre",
    "language": "language",
    "length": None,
    "originaldate": "date",
    "performer": "performer",
    "releasecountry": "comment",
    "title": "title",
    "tracknumber": "track"
}

METADATA_TAGS = list(EasyID3.valid_keys.keys())
METADATA_TAGS.sort()

AVAILABLE_INFO = [
    'categories',
    'channel',
    'description',
    'duration',
    'fulltitle',
    'id',
    'original_url',
    'playlist',
    'playlist_index',
    'tags',
    'thumbnail',
    'title',
    'upload_date',
    'uploader',
    'uploader_url',
    'webpage_url'
]


class MetadataPostProcessor(PostProcessor):

    def __init__(self, data=None, on=True, downloader=None):
        super().__init__(downloader)
        if data is None:
            self.data = {}
        else:
            self.data = data
        self.on = on

    def run(self, info):
        if self.on:
            parser = Parser(info)

            tags = None
            match info["ext"]:
                case "wav" | "wave" | "mp3" | "ac3" | "aac" | "tta" | "aif" | "aiff":
                    try:
                        tags = EasyID3(info['filepath'])
                    except mutagen.id3.ID3NoHeaderError:
                        tags = mutagen.File(info['filepath'], easy=True)
                        tags.add_tags()
                case "flac":
                    tags = FLAC(info['filepath'])
                    if not tags.tags:
                        tags.add_tags()
                case "mp4" | "m4a":
                    tags = EasyMP4(info['filepath'])
                case _:
                    self.ffmpeg_metadata(info, parser)
                    return [], info

            for key, value in self.data.items():
                tags[key] = parser.parse(value)
            tags.save()

        return [], info

    def ffmpeg_metadata(self, info, parser):
        tags = ''

        def converter(value):
            return parser.parse(value)

        for key, value in self.data.items():
            if value is not None:
                tags += f' {converter(key)}="{parser.parse(value)}"'

        proc = subprocess.Popen(f'"{join(application_path, "bin", "ffmpeg")}" '
                                f'-y -i "{info["filepath"]}" '
                                f'-c copy -metadata{tags}')
        proc.wait()
