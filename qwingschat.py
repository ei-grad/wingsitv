#!/usr/bin/env python3
# coding: utf-8

from time import time
from datetime import datetime
from urllib.error import URLError

from PyQt4.QtCore import Qt
from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4.QtWebKit import QWebView

from settings import config, save_config

from wingschat import *


class QWingsChatLineEdit(QtGui.QLineEdit):


    def __init__(self, login, parent=None):
        super(QWingsChatLineEdit, self).__init__(parent)
        self.parent = parent
        self.history = []
        self.history_index = 0
        self.login = login

    def keyPressEvent(self, event):

        msg = self.text()
        key = event.key()

        if key == Qt.Key_Up:
            if self.history_index < len(self.history) -1:
                self.history_index += 1
                self.setText(self.history[self.history_index])
                event.accept()
            else:
                event.ignore()
        elif key == Qt.Key_Down:
            if self.history_index > 0:
                self.history_index -= 1
                self.setText(self.history[self.history_index])
                event.accept()
            else:
                event.ignore()
        elif key == Qt.Key_Return:
            try:
                send_message(self.login, msg)
                self.history_index = len(self.history)
                self.history.append(msg)
                self.clear()
            except:
                QtGui.QMessageBox("Ошибка", "Не удалось отправить сообщение!").show()
            event.accept()
        else:
            super(QWingsChatLineEdit, self).keyPressEvent(event)

class QWingsChat(QtGui.QWidget):

    def __init__(self, parent=None, app=None):

        super(QWingsChat, self).__init__(parent)

        self.app = app
        self.error = 0

        self.setWindowTitle('КрыльяITV :: Чат')

        self.parser = ChatMsgParser()
        self.template = open('chattemplate.html').read()

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
        self.message = QWingsChatLineEdit(login)

        vb = QtGui.QVBoxLayout()
        vb.setMargin(5)
        vb.setSpacing(0)
        vb.addWidget(self.chat)
        vb.addWidget(self.message)
        self.setLayout(vb)

        self.chat.setHtml(self.template)

        self.timer = QtCore.QTimer()
        self.timer.singleShot(0, self.update_chat)
        #QtCore.QObject.connect(self.timer, QtCore.SIGNAL("timeout()"),
        #        self.update_chat)
        #self.timer.start(1000)

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

    def update_chat(self):
        mf = self.chat.page().mainFrame()
        try:
            for msg in self.parser.parse(get_messages()):
                mf.findFirstElement("ul").appendInside(self.format_msg(msg))
                mf.scrollToAnchor("bottom")
            if self.error > 0:
                if self.error >= 5:
                    mf.findFirstElement("ul").appendInside(
                            '<li>({}) Подключение восстановлено.</li>'.format(
                                datetime.now().time().strftime("%H:%M:%S")))
                self.error = 0
        except:
            self.error += 1
            if self.error == 5:
                mf.findFirstElement("ul").appendInside(
                        '<li>({}) Проблема с подключением.</li>'.format(
                            datetime.now().time().strftime("%H:%M:%S")))
        self.timer.singleShot(1000, self.update_chat)


    def closeEvent(self, event):
        if self.app is not None:
            self.app.toggle_chat()
            event.ignore()
        else:
            super(QWingsChat, self).closeEvent(event)

