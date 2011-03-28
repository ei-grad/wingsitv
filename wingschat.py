#!/usr/bin/env python3
# coding: utf-8

from urllib.request import urlopen
from urllib.parse import urlencode
from random import randint

def send_message(nick, message, uid=2303):
    urlopen('http://torrent.mnx.net.ru/ajaxchat/sendChatData.php',
            data=bytes(urlencode({
                'n': nick,
                'c': message,
                'u': uid}), 'utf-8'))

def get_messages(lastid=-1):
    return urlopen('http://torrent.mnx.net.ru/ajaxchat/getChatData.php?lastID=%d&rand=%d' % (lastid, randint(0, 1000000))).read().decode('utf-8')

