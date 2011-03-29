#!/usr/bin/env python3
# coding: utf-8

from urllib.request import urlopen
from urllib.parse import urlencode
from random import randint
from datetime import datetime

def send_message(nick, message, uid=2303):
    urlopen('http://torrent.mnx.net.ru/ajaxchat/sendChatData.php',
            data=bytes(urlencode({
                'n': nick,
                'c': message,
                'u': uid}), 'utf-8'))

def get_messages(lastid=-1):
    return urlopen('http://torrent.mnx.net.ru/ajaxchat/getChatData.php?lastID=%d&rand=%d' % (lastid, randint(0, 1000000))).read().decode('utf-8')

class ChatMsgParser(object):

    def __init__(self):
        #super(ChatMsgParser, self).__init__(*args, **kwargs)

        self.ids = set()
        self.msgs = []

    def parse(self, text):

        new_msgs = []
        raw_msgs = text.strip().split('<li>')[1:]

        for raw in raw_msgs:
            p = raw.find("# ") + 2
            msg_id = int(raw[p:raw.find('</div>', p)])
            if msg_id in self.ids:
                continue
            self.ids.add(msg_id)
            msg = {}
            msg['id'] = msg_id
            msg['datetime'] = datetime.strptime(raw[19:38],'%d/%m/%Y %H:%M:%S')
            msg['nickname'] = raw[raw.find('>', 79)+1:raw.find('</a>', 79)]
            s = "<div class='chatoutput'>"
            p = raw.find(s, p) + len(s)
            msg['message'] = raw[p:raw.find("</div>", p)]
            self.msgs.append(msg)
            new_msgs.append(msg)

        return new_msgs

