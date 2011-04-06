# coding: utf-8
#
# Copyright 2011, Novikov Valentin

__all__ = [ 'QTrafView' ]

import sqlite3
from os.path import join
from PyQt4 import QtCore, QtGui
from PyQt4.QtGui import QTableWidgetItem
from settings import DEFAULT_WORKDIR

dbfile = join(DEFAULT_WORKDIR, 'sqlite.db')
ipath = join('share', '22')

class tvDateEdit(QtGui.QDateEdit):
  """ QDateEdit + QCalendar """

  def __init__(self, parent):
    super(tvDateEdit, self).__init__(parent)

    self.setDateRange(QtCore.QDate(2008, 1, 1),
                      QtCore.QDate(2020, 1, 1))

    self.setDate(QtCore.QDate().currentDate())
    self.setDisplayFormat("dd.MM.yyyy")

    self.setCalendarPopup(True)
    self.setCalendarWidget(QtGui.QCalendarWidget(self))

  def __str__(self):
    return self.date().toString("dd.MM.yyyy")

class tvTimeEdit(QtGui.QTimeEdit):

  def __init__(self, parent=None, hour=-1):
    super(tvTimeEdit, self).__init__(parent)
    if hour < 0 or hour > 23:
      self.setTime(QtCore.QTime().currentTime())
    else:
      self.setTime(QtCore.QTime(hour, 0))

  def __str__(self):
    return "{}".format(self.time().toString("h"))

  def __eq__(self, obj):
    return str(self) == str(obj)

class tvTable(QtGui.QTableWidget):
  labels = ('Дата', 'Время', 'Объем')
  backcolor = QtGui.QColor(227, 227, 227)

  def __init__(self, parent=None):
    super(tvTable, self).__init__(parent)
    self.parent = parent
    self.sqlconn = None
    self.curs = None
    self.myclear()

  def myclear(self):
    self.clear()
    self.setRowCount(1)
    self.setColumnCount(len(self.labels))
    self.setHorizontalHeaderLabels(self.labels)

  def refresh(self, dateSE, timeSE):
    if not self.sqlconn:
      self.sqlconn = sqlite3.connect(dbfile)
      self.curs = self.sqlconn.cursor()

    if not self.sqlconn or not self.curs:
      return

    ttype = "amounts_in" if str(self.parent.comboTrafType) == '0' else "amounts_out"
    q = "SELECT date,hour,amount FROM '{}' WHERE date > '{}'"
    q+= " AND date < '{}' AND hour > '{}' AND hour < '{}'"
    q = q.format(ttype, dateSE[0], dateSE[1], timeSE[0], timeSE[1])
    self.curs.execute(q)
    #print("debug", ttype, q)

    irow = 1
    fullsum = 0
    self.myclear()
    for row in self.curs:
      self.setRowCount(irow + 1)
      fullsum += row[2]
      d = QTableWidgetItem(str(row[0]))
      h = QTableWidgetItem("{:02}:00".format(row[1]))

      s = QTableWidgetItem(self.parent.comboTrafSize.calc(row[2]))
      i = self.parent.comboTrafType.items[int(str(self.parent.comboTrafType))][1]
      s.setIcon(QtGui.QIcon(join(ipath, i)))

      if not irow % 2 == 0:
        d.setBackgroundColor(self.backcolor)
        h.setBackgroundColor(self.backcolor)
        s.setBackgroundColor(self.backcolor)
      
      self.setItem(irow, 0, d)
      self.setItem(irow, 1, h)
      self.setItem(irow, 2, s)
      irow += 1

    s = QTableWidgetItem("Итого:")
    s.setTextAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
    self.setItem(0, 1, s)

    s = QTableWidgetItem(self.parent.comboTrafSize.calc(fullsum))
    s.setForeground(QtGui.QBrush(QtGui.QColor(244, 0, 0)))
    self.setItem(0, 2, s)

class tvComboTrafType(QtGui.QComboBox):
  items = (('Входящий', 'left.png'),
          ('Исходящий', 'right.png'))

  def __init__(self, parent=None):
    super(tvComboTrafType, self).__init__(parent)

    self.clear()
    [ self.addItem(QtGui.QIcon(join(ipath, i[1])), i[0]) for i in self.items ]

  def __str__(self):
    return str(self.currentIndex())

class tvComboTrafSize(QtGui.QComboBox):
  items = ('b', 'Kb', 'Mb', 'Gb')

  def __init__(self, parent=None):
    super(tvComboTrafSize, self).__init__(parent)

    self.clear()
    [ self.addItem(i) for i in self.items ]
    self.setCurrentIndex(2)

  def calc(self, size):
    for i in range(self.currentIndex()):
      size /= 1024
    return "{:.4f}".format(size)

  def __str__(self):
    i, r = len(self.items[1:]) - self.currentIndex(), 1
    for i in range(i):
      r *= 1024
    return str(r)

class tvToolSync(QtGui.QToolButton):

  def __init__(self, parent=None):
    super(tvToolSync, self).__init__(parent)
    self.setIcon(QtGui.QIcon(join(ipath, 'sync.png')))
    self.setToolTip("Синхронизироваться с сервером")
    self.clicked.connect(self.__sync)

  def __sync(self):
    QtGui.QMessageBox.critical(self, "Ахтунг", "Синхронизация в доработке")
    self.setVisible(False)

class QTrafView(QtGui.QWidget):

  def __init__(self, parent=None):
    super(QTrafView, self).__init__(parent)
    vboxRoot = QtGui.QVBoxLayout(self)

    ## dates
    hboxDRange = QtGui.QHBoxLayout()
    hboxDRange.addWidget(QtGui.QLabel("Интервал дат", self))
    self.dateS = tvDateEdit(self)
    self.dateE = tvDateEdit(self)
    self.pushSync = tvToolSync(self)

    hboxDRange.addWidget(self.dateS)
    hboxDRange.addWidget(self.dateE)
    hboxDRange.addWidget(self.pushSync)

    ## times
    hboxTRange = QtGui.QHBoxLayout()
    hboxTRange.addWidget(QtGui.QLabel("Интервал время", self))
    self.timeS = tvTimeEdit(self, 0)
    self.timeE = tvTimeEdit(self)
    hboxTRange.addWidget(self.timeS)
    hboxTRange.addWidget(self.timeE)

    ## table
      # ::panel
    hboxTablePanel = QtGui.QHBoxLayout()
    hboxTablePanel.addWidget(QtGui.QLabel("Трафик", self))
    self.comboTrafType = tvComboTrafType(self)
    self.comboTrafSize = tvComboTrafSize(self)
    hboxTablePanel.addWidget(self.comboTrafType)
    hboxTablePanel.addWidget(self.comboTrafSize)
      #
    vboxTable = QtGui.QVBoxLayout()
    self.table = tvTable(self)
    vboxTable.addLayout(hboxTablePanel)
    vboxTable.addWidget(self.table)

    ##
    vboxRoot.addLayout(hboxDRange)
    vboxRoot.addLayout(hboxTRange)
    vboxRoot.addLayout(vboxTable)

    #
    self.setLayout(vboxRoot)
    self.setWindowTitle("Обзор трафика")

    ## SIGNALs
    self.timeS.timeChanged.connect(self.__timeCheck)
    self.timeE.timeChanged.connect(self.__timeCheck)
    self.dateS.dateChanged.connect(self.__timeCheck)
    self.dateE.dateChanged.connect(self.__timeCheck)
    self.comboTrafType.currentIndexChanged.connect(self.__timeCheck)
    self.comboTrafSize.currentIndexChanged.connect(self.__timeCheck)

  __lockQuery = False
  def __timeCheck(self):
    self.__lockQuery = self.timeS == self.timeE
    if self.__lockQuery:
      self.setWindowTitle("Ааай, проверьте интервалы! ;)")

    else:
      self.setWindowTitle("Обзор трафика от {} по {}".format(str(self.dateS),str(self.dateE)))
      self.table.refresh(
          (str(self.dateS), str(self.dateE)),
          (str(self.timeS), str(self.timeE)))

