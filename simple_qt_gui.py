#!/usr/bin/python
# coding: utf-8

import sys, os
from time import time

from PyQt4 import QtGui
from PyQt4 import QtCore

from settings import config, save_config

from utm5client import UTM5Client
from qwingschat import QWingsChat
from qtrafview import QTrafView

class QUtm5Gui(QtGui.QApplication):
    def __init__(self, argv):

        super(QUtm5Gui, self).__init__(argv)

        if config['utm5']['login'] is None or config['utm5']['passwd'] is None:
            self.login_dialog()

        self.utm5client = UTM5Client(auto_auth=True)

        self.chat = QWingsChat(app=self)
        self.traf = QTrafView()
        if config['chat']['show'] == "True":
            self.chat.show()

        self.trayIcon = QtGui.QSystemTrayIcon()
        self.trayIcon.setIcon(QtGui.QIcon(os.path.join(os.path.dirname(__file__), 'wings_logo.png')))
        self.trayIcon.setVisible(True)
        self.connect(self.trayIcon,
                QtCore.SIGNAL("activated(QSystemTrayIcon::ActivationReason)"),
                self.on_sys_tray_activated)

        self.trayIconMenu = QtGui.QMenu()

        act = self.trayIconMenu.addAction("Чат")
        self.connect(act, QtCore.SIGNAL("triggered()"), self.toggle_chat)

        act = self.trayIconMenu.addAction("Трафик")
        self.connect(act, QtCore.SIGNAL("triggered()"), self.toggle_traffic)

        self.trayIconMenu.addSeparator()

        act = self.trayIconMenu.addAction("Выход")
        self.connect(act, QtCore.SIGNAL("triggered()"), self.quit)

        self.trayIcon.setContextMenu(self.trayIconMenu)

        self.update_tooltip_timer = QtCore.QTimer()
        self.update_tooltip_timer.singleShot(0, self.update_tooltip)
        QtCore.QObject.connect(self.update_tooltip_timer,
                QtCore.SIGNAL("timeout()"), self.update_tooltip)
        self.update_tooltip_timer.start(1000*60*5) # 5 minutes

    def login_dialog(self):
        while True:
            config['utm5']['login'], ok1 = QtGui.QInputDialog.getText(None,
                   'Вход в личный кабинет', 'Введите логин:')
            config['utm5']['passwd'], ok2 = QtGui.QInputDialog.getText(None,
                   'Вход в личный кабинет', 'Введите пароль:')
            if ok1 and ok2: break
        save_config()

    def update_tooltip(self):

        daytime, full = self.utm5client.get_month_traffic()

        def hum(size):
            return '%.2f МиБ' % (float(size)/(2**20),)

        self.trayIcon.setToolTip(('<h3>Трафик</h3>'
            '<table>'
            '<tr>'
                '<th></th>'
                '<th>Входящий</th>'
                '<th>Исходящий</th>'
            '</tr>'
            '<tr>'
                '<td>Дневной:</td>'
                '<td>%s</td>'
                '<td>%s</td>'
            '</tr>'
            '<tr>'
                '<td>Полный:</td>'
                '<td>%s</td>'
                '<td>%s</td>'
            '</tr>'
            '</table>') % tuple(map(hum, daytime + full)))

    def toggle_chat(self):
        self.chat.setVisible(not self.chat.isVisible())
        config['chat']['show'] = str(self.chat.isVisible())
        save_config()

    def toggle_traffic(self):
        self.traf.setVisible(not self.traf.isVisible())

    def on_sys_tray_activated(self, reason):
        if reason == QtGui.QSystemTrayIcon.Trigger: # click
            self.toggle_chat()

if __name__ == "__main__":
    sys.exit(QUtm5Gui(sys.argv).exec_())

