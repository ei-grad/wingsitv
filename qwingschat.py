#!/usr/bin/env python3
# coding: utf-8


from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4.QtWebKit import QWebView

from wingschat import *


class QWingsChat(QtGui.QWidget):

    def __init__(self, parent=None):

        super(QWingsChat, self).__init__(parent)

        self.setGeometry(300, 300, 250, 150)
        self.setWindowTitle('КрыльяITV')

        self.parser = ChatMsgParser()
        self.template = open('chattemplate.html').read()

        self.messages = QWebView()
        self.post_input = QtGui.QLineEdit()
        self.post_button = QtGui.QPushButton("Отправить")
        self.userlist = QtGui.QListView()

        wr = QtGui.QHBoxLayout()
        vb = QtGui.QVBoxLayout()
        wr.addLayout(vb)
        wr.addWidget(self.userlist)

        vb.addWidget(self.messages)

        hb = QtGui.QHBoxLayout()
        hb.addWidget(self.post_input)
        hb.addWidget(self.post_button)

        vb.addLayout(hb)

        self.setLayout(wr)

        self.timer = QtCore.QTimer()
        self.timer.singleShot(0, self.update_chat)
        QtCore.QObject.connect(self.timer, QtCore.SIGNAL("timeout()"), self.update_chat)
        self.timer.start(1000)

        self.show()

    def update_chat(self):
        self.parser.parse(get_messages())
        self.template = open('chattemplate.html').read()
        self.messages.setHtml(self.template % "\n".join([ "<tr><td>{}</td><td class='nick'>{}:</td><td>{}</td></tr>".format(d['datetime'].time(), d['nickname'], d['message']) for d in self.parser.msgs ]))

