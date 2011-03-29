#!/usr/bin/python
# coding: utf-8

import sys, os
from time import time

from PyQt4 import QtGui
from PyQt4 import QtCore

from utm5client import UTM5Client, config, save_config
from qwingschat import QWingsChat


class QUtm5Gui(QtGui.QApplication):
    def __init__(self, argv):

        super(QUtm5Gui, self).__init__(argv)

        if 'auth' not in config or config['auth']['passwd'] is None:
            self.login_dialog()
        self.utm5client = UTM5Client(auto_auth=True)
        if 'auth' not in config or config['auth']['passwd'] is None:
            self.login_dialog()
        self.utm5client = UTM5Client(auto_auth=True)

        if 'qutm5client' not in config:
            config['qutm5client'] = {
                    'show_chat': True,
                    'show_traffic': False
                }

        self.chat = QWingsChat()
        print(config['qutm5client']['show_chat'])
        if config['qutm5client']['show_chat'].bool() == True:
            self.chat.show()

        self.trayIcon = QtGui.QSystemTrayIcon()
        self.trayIcon.setIcon(QtGui.QIcon('wings_logo.png'))
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
        QtCore.QObject.connect(self.update_tooltip_timer, QtCore.SIGNAL("timeout()"), self.update_tooltip)
        self.update_tooltip_timer.start(1000*60*5) # 5 minutes

    def login_dialog(self):
        raise NotImplementedError()

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
        config['qutm5client']['show_chat'] = str(self.chat.isVisible())
        save_config()

    def toggle_traffic(self):
        pass

    def on_sys_tray_activated(self, reason):
        if reason == QtGui.QSystemTrayIcon.Trigger: # click
            self.toggle_chat()

if __name__ == "__main__":
    sys.exit(QUtm5Gui(sys.argv).exec_())

