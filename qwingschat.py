#!/usr/bin/env python3
# coding: utf-8


from PyQt4.QtCore import Qt
from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4.QtWebKit import QWebView

from utm5client import config, save_config, DEFAULT_WORKDIR
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
            send_message(self.login, msg)
            self.history_index = len(self.history)
            self.history.append(msg)
            self.clear()
            event.accept()
        else:
            super(QWingsChatLineEdit, self).keyPressEvent(event)

class QWingsChat(QtGui.QWidget):

    def __init__(self, parent=None, app=None):

        super(QWingsChat, self).__init__(parent)

        self.app = app

        self.setWindowTitle('КрыльяITV :: Чат')

        self.parser = ChatMsgParser()
        self.template = open('chattemplate.html').read()

        if 'chat' not in config:
            while True:
                login, ok = QtGui.QInputDialog.getText(self, 'Вход', 'Выберите имя:')
                if ok:
                    break
            config['chat'] = {'login': login}
            save_config()
        else:
            login = config['chat']['login']

        self.chat = QWebView()
        self.message = QWingsChatLineEdit(login)

        vb = QtGui.QVBoxLayout()
        vb.addWidget(self.chat)
        vb.addWidget(self.message)
        self.setLayout(vb)

        self.parser.parse(get_messages())

        self.chat.setHtml(self.template % "\n".join([ self.format_msg(msg)
            for msg in self.parser.msgs ]))

        self.timer = QtCore.QTimer()
        QtCore.QObject.connect(self.timer, QtCore.SIGNAL("timeout()"),
                self.update_chat)
        self.timer.start(1000)

    def format_msg(self, msg):
        return "<li>({}) {}: {}</li>".format(msg['datetime'].time(),
                msg['nickname'], msg['message'])

    def update_chat(self):
        for msg in self.parser.parse(get_messages()):
            self.chat.page().mainFrame().findFirstElement("ul").appendInside(
                    self.format_msg(msg))


    def closeEvent(self, event):
        if self.app is not None:
            self.app.toggle_chat()
            #self.hide()
            event.ignore()
        else:
            super(QWingsChat, self).closeEvent(event)

