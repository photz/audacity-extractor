#!/usr/bin/env python3

import subprocess
from argparse import ArgumentParser
import logging, csv
from collections import namedtuple
import os.path
from typing import Generator

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

Label = namedtuple('Label', ['start', 'duration', 'text'])

def labels(path: str) -> Generator[Label, None, None]:
    with open(path) as f:
        reader = csv.reader(f, delimiter='\t')
        for start_s, end_s, text in reader:
            start = float(start_s)
            end = float(end_s)
            duration = end - start
            yield Label(start=start,
                        duration=duration,
                        text=text)


def extract(old: str, new: str, start: float, duration: float):
    bitrate = 320
    retval = subprocess.call([
        'sox',
        old,
        '-C', str(bitrate),
        new,
        'trim',
        str(start),
        str(duration)
    ])
    if retval != 0: raise Exception('sox returned {}'.format(retval))


def tag(path: str, artist=None, title=None, album=None, track:int=None):
    cmd = ['mid3v2']

    if artist:
        cmd.extend(['-a', artist])

    if title:
        cmd.extend(['-T', title])

    if album:
        cmd.extend(['-A', album])

    if track:
        cmd.extend(['-T', str(track)])

    cmd.append(path)

    retval = subprocess.call(cmd)

    if retval != 0: raise Exception('mid3v2 subprocess retured {}'.format(retval))
    


def main():
    parser = ArgumentParser()

    parser.add_argument('labels')
    parser.add_argument('audiofile')
    parser.add_argument('target_dir')
    parser.add_argument('--artist', default=None)
    parser.add_argument('--album', default=None)

    args = parser.parse_args()

    for track, label in enumerate(labels(args.labels), 1):

        new_name = '{0:02d}.mp3'.format(track)

        dest = os.path.join(args.target_dir, new_name)

        logger.info('Creating {}'.format(dest))

        extract(args.audiofile, dest, label.start, label.duration)

        logger.info('Tagging {}'.format(dest))

        tag(dest,
            artist=args.artist,
            title=label.text,
            album=args.album,
            track=track)
    

if __name__ == '__main__':
    main()
