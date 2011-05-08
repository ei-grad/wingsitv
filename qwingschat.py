#!/usr/bin/env python3
# coding: utf-8

import os
from datetime import datetime
from urllib.parse import urlencode
from urllib.error import URLError
from random import randint
import socket

from PyQt4.QtCore import Qt
from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4.QtWebKit import QWebView
from PyQt4.QtNetwork import QHttp, QHttpRequestHeader

from settings import config, save_config
from wingschat import ChatMsgParser


class QWingsChatLineEdit(QtGui.QLineEdit):

    def __init__(self, login, uid=2303, parent=None):
        super(QWingsChatLineEdit, self).__init__(parent)
        self.parent = parent
        self.history = ['']
        self.history_index = 0
        self.login = login
        self.uid = uid
        self.http = QHttp('torrent.mnx.net.ru')
        self.http_header = QHttpRequestHeader("POST", "/ajaxchat/sendChatData.php")
        self.http_header.setValue('Host', 'torrent.mnx.net.ru')
        self.http_header.setContentType("application/x-www-form-urlencoded")
        self.connect(self.http, QtCore.SIGNAL("requestFinished(int,bool)"), self.postCompleted)

    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_Up:
            if self.history_index < len(self.history) - 1:
                self.history_index += 1
                self.setText(self.history[self.history_index])
            event.accept()
        elif key == Qt.Key_Down:
            if self.history_index > 0:
                self.history_index -= 1
                self.setText(self.history[self.history_index])
            event.accept()
        elif key == Qt.Key_Return:
            msg = str(self.text())
            if msg:
                data = bytes(urlencode({'n': self.login,'c': msg,'u': self.uid}), 'utf-8')
                self.http.request(self.http_header, data);
                if len(self.history) == 1 or msg != self.history[1]:
                    self.history[0] = msg
                    self.history_index = 0
                    self.history.insert(0, '')
                self.clear()
            event.accept()
        else:
            super(QWingsChatLineEdit, self).keyPressEvent(event)
            if self.history_index == 0:
                self.history[0] = self.text()

    def postCompleted(self, msgid, error):
        if error:
            m = QtGui.QMessageBox()
            m.setText("Не удалось отправить сообщение!")
            m.exec()

class QWingsChat(QtGui.QWidget):

    def __init__(self, parent=None, app=None):

        super(QWingsChat, self).__init__(parent)

        self.app = app
        self.error = 0

        self.setWindowTitle('КрыльяITV :: Чат')
        self.setWindowIcon(QtGui.QIcon(os.path.join(os.path.dirname(__file__), 'wings_logo.png')))

        self.parser = ChatMsgParser()
        self.template = open(os.path.join(os.path.dirname(__file__), 'chattemplate.html')).read()

        if config['chat']['login'] is None:
            while True:
                login, ok = QtGui.QInputDialog.getText(self, 'Вход в чат', 'Выберите имя:')
                if ok:
                    break
            config['chat']['login'] = login
            save_config()
        else:
            login = config['chat']['login']

        self.chat = QWebView()
        self.chat.setContextMenuPolicy(QtCore.Qt.PreventContextMenu)
        self.message = QWingsChatLineEdit(login)

        vb = QtGui.QVBoxLayout()
        vb.setMargin(0)
        vb.setSpacing(0)
        vb.addWidget(self.chat)
        vb.addWidget(self.message)
        self.setLayout(vb)

        self.chat.setHtml(self.template)

        self.http = QHttp('torrent.mnx.net.ru')
        self.connect(self.http, QtCore.SIGNAL("done(bool)"), self.update_chat)

        self.timer = QtCore.QTimer()
        self.timer.singleShot(0, self.send_update_request)

    def format_msg(self, msg):
        def get_color(nick):
            m = 12345
            for i in nick:
                m *= ord(i)
            d = 190
            r = m % d; m /= d
            g = m % d; m /= d
            b = m % d; m /= d
            return "#%.2X%.2X%.2X" % (r, g, b)
        return '<li>({}) <span style="color:{};">{}:</span> {}</li>'.format(msg['datetime'].time(),
                get_color(msg['nickname']), msg['nickname'], msg['message'])

    def send_update_request(self):
        self.http.get('/ajaxchat/getChatData.php?lastID=-1&rand=%d' % randint(0, 1000000))

    def update_chat(self, error):
        data = str(self.http.readAll(), 'utf-8')
        if not error:
            mf = self.chat.page().mainFrame()
            if self.error > 0:
                if self.error >= 30:
                    mf.findFirstElement("ul").appendInside(
                            '<li style="color: gray;">({}) Подключение восстановлено.</li>'.format(
                                datetime.now().time().strftime("%H:%M:%S")))
                self.error = 0
            msgs = self.parser.parse(data)
            for msg in msgs:
                mf.findFirstElement("ul").appendInside(self.format_msg(msg))
                mf.scrollToAnchor("bottom")

        else:
            self.error += 1
            if self.error == 30:
                mf.findFirstElement("ul").appendInside(
                        '<li style="color: gray;">({}) Проблема с подключением.</li>'.format(
                            datetime.now().time().strftime("%H:%M:%S")))
        self.timer.singleShot(1000, self.send_update_request)


    def closeEvent(self, event):
        if self.app is not None:
            self.app.toggle_chat()
            event.ignore()
        else:
            super(QWingsChat, self).closeEvent(event)

