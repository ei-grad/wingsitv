#!/usr/bin/env python2

import sys, os, re, logging, locale

from time import time, sleep
from datetime import datetime

import Image, ImageDraw, ImageFont
from urllib import urlopen
from StringIO import StringIO

def wcd(tmp_dir, fps, font):
    while True:
        next_tick_at = (int(time() * fps) + 1) / fps
        try:
            img = Image.open(StringIO(urlopen(
                    'http://v.mnx.net.ru/web_play/real_pic.php?par=0'
                ).read()))

            text = datetime.now().strftime('%c').decode('utf-8')
            draw = ImageDraw.Draw(img)
            draw.text((img.size[0] - 350, img.size[1] - 30),
                    text, font=font, fill='rgb(255,255,0)')
            del draw

            img.save(os.path.join(tmp_dir, str(int(time() * 10)) + '.jpg'))
            del img
        except Exception as e:
            logging.error(e)
        dt = next_tick_at - time()
        if dt > 0:
            sleep(dt)

if __name__ == "__main__":

    using = """
    python %s <tmp_dir>
    """ % sys.argv[0]

    if len(sys.argv) != 2:
        sys.stderr.write(using)

    locale.setlocale(locale.LC_ALL, locale.getdefaultlocale())

    TEMPDIR = sys.argv[1]
    FPS = 3
    FONT = ImageFont.truetype(os.popen("fc-list '' file | grep -i mono").readline().strip(': \n'), 24)

    if not os.path.exists(TEMPDIR):
        os.mkdir(TEMPDIR)


    from daemon import DaemonContext
    with DaemonContext():
        logging.basicConfig(filename='/var/log/camdaemon.log', level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(funcName)s: %(message)s")
        wcd(TEMPDIR, FPS, FONT)

