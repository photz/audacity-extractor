#!/usr/bin/env python3

import subprocess
from argparse import ArgumentParser
import logging, re
from collections import namedtuple
import os.path

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

Label = namedtuple('Label', ['start', 'end', 'text'])

def labels(path: str):
    contents = None
    with open(path) as f:
        contents = f.read()

    it = re.finditer('(\d+\.\d+)\t(\d+\.\d+)\t([^\n]*)', contents)

    for label in it:
        yield Label(start=float(label.group(1)),
                    end=float(label.group(2)),
                    text=label.group(3))


def extract(old: str, new: str, start: float, duration: float):
    bitrate = 320
    subprocess.call([
        'sox',
        old,
        '-C', str(bitrate),
        new,
        'trim',
        str(start),
        str(duration)
    ])


def tag(path: str, artist=None, title=None, album=None, track=None):
    cmd = ['mid3v2']

    if artist:
        cmd.extend(['-a', artist])

    if title:
        cmd.extend(['-T', title])

    if album:
        cmd.extend(['-A', album])

    if track:
        cmd.extend(['-T', track])

    cmd.append(path)

    subprocess.call(cmd)


def main():
    parser = ArgumentParser()

    parser.add_argument('labels')
    parser.add_argument('audiofile')
    parser.add_argument('target_dir')
    parser.add_argument('--artist', default=None)
    parser.add_argument('--album', default=None)

    args = parser.parse_args()

    for i, label in enumerate(labels(args.labels), 1):

        new_name = '{0:02d}.mp3'.format(i)

        dest = os.path.join(args.target_dir, new_name)

        duration = label.end - label.start

        logger.info('Creating {}'.format(dest))

        extract(args.audiofile, dest, label.start, duration)

        logger.info('Tagging {}'.format(dest))

        tag(dest,
            artist=args.artist,
            title=str(i),
            album=args.album)
    

if __name__ == '__main__':
    main()
