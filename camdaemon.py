#!/usr/bin/env python2
#
#   Copyright (c) 2010-2011, Andrew Grigorev <andrew@ei-grad.ru>
#   All rights reserved.
#
#   Redistribution and use in source and binary forms, with or without
#   modification, are permitted provided that the following conditions are
#   met:
#
#       Redistributions of source code must retain the above copyright notice,
#       this list of conditions and the following disclaimer.  Redistributions
#       in binary form must reproduce the above copyright notice, this list of
#       conditions and the following disclaimer in the documentation and/or
#       other materials provided with the distribution.  Neither the name of
#       the <ORGANIZATION> nor the names of its contributors may be used to
#       endorse or promote products derived from this software without
#       specific prior written permission.
#
#   THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
#   IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
#   THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
#   PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
#   CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
#   EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
#   PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
#   PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
#   LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
#   NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
#   SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

"""
Grabs image from webcam 3 times per second.
"""

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

    TEMPDIR = sys.argv[1]
    FPS = 3
    FONT = ImageFont.truetype(os.popen("fc-list '' file | grep -i mono | grep -iv oblique").readline().strip(': \n'), 24)

    if not os.path.exists(TEMPDIR):
        os.mkdir(TEMPDIR)

    from daemon import DaemonContext
    with DaemonContext():
        locale.setlocale(locale.LC_ALL, locale.getdefaultlocale())
        logging.basicConfig(filename='/var/log/camdaemon.log', level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(funcName)s: %(message)s")
        wcd(TEMPDIR, FPS, FONT)

