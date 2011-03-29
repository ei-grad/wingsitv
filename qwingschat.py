#!/usr/bin/env python3
# coding: utf-8


from PyQt4 import QtGui
from PyQt4 import QtCore

from wingschat import *


class QWingsChat(QtGui.QWidget):
    def __init__(self, parent=None):
        super(QWingsChat, self).__init__(parent)
        self.setGeometry(300, 300, 250, 150)
        self.setWindowTitle('КрыльяITV')

