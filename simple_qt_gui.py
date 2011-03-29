#!/usr/bin/python

import sys
from PyQt4 import QtGui
from PyQt4 import QtCore

from utm5client import UTM5Client


class QUtm5Gui(QtGui.QWidget):
    def __init__(self, parent=None):

        self.utm5client = UTM5Client(auto_auth=True)

        QtGui.QWidget.__init__(self, parent)

        self.setGeometry(300, 300, 250, 150)
        self.setWindowTitle('КрыльяITV')

        self.trayIcon = QtGui.QSystemTrayIcon(self)
        self.trayIcon.setIcon(QtGui.QIcon('wings_logo.png'))
        self.trayIcon.setVisible(True)
        self.connect(self.trayIcon, QtCore.SIGNAL("activated(QSystemTrayIcon::ActivationReason)"), self.on_sys_tray_activated)

        self.trayIconMenu = QtGui.QMenu(self)
        quit_act = self.trayIconMenu.addAction("Выход")
        QtCore.QObject.connect(quit_act, QtCore.SIGNAL("triggered()"), app, QtCore.SLOT("quit()"))
        self.trayIcon.setContextMenu(self.trayIconMenu)

        self.update_tooltip_timer = QtCore.QTimer()
        self.update_tooltip_timer.singleShot(0, self.update_tooltip)
        QtCore.QObject.connect(self.update_tooltip_timer, QtCore.SIGNAL("timeout()"), self.update_tooltip)
        self.update_tooltip_timer.start(1000*60*5) # 5 minutes


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

    def on_sys_tray_activated(self, reason):
        if reason == QtGui.QSystemTrayIcon.Trigger: # click
            self.setVisible(not self.isVisible())

    def okayToClose(self):
        return False

    def closeEvent(self, event):
        if self.okayToClose():
            #user asked for exit
            self.trayIcon.hide()
            event.accept()
        else:
            #"minimize"
            self.hide()
            #self.trayIcon.show() #thanks @mojo
            event.ignore()

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = QUtm5Gui()
    window.show()
    sys.exit(app.exec_())

