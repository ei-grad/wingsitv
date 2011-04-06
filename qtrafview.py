# coding: utf-8
#
# Copyright 2011, Novikov Valentin

__all__ = [ 'QTrafView' ]

import sqlite3
from PyQt4 import QtCore, QtGui

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

class tvTimeEdit(QtGui.QTimeEdit):
  
  def __init__(self, parent=None):
    super(tvTimeEdit, self).__init__(parent)
    self.setTime(QtCore.QTime().currentTime())
  
  def __str__(self):
    return "{}:00".format(self.time().toString("hh"))

  def __eq__(self, obj):
    return str(self) == str(obj)

class tvTable(QtGui.QTableWidget):
  labels = ('Дата', 'Время', 'Объем')

  def __init__(self, parent=None):
    super(tvTable, self).__init__(parent)
    self.myclear()

  def myclear(self):
    self.clear()
    self.setRowCount(1)
    self.setColumnCount(len(self.labels))
    self.setHorizontalHeaderLabels(self.labels)

class tvComboTrafType(QtGui.QComboBox):
  items = ('Входящий', 'Исходящий')

  def __init__(self, parent=None):
    super(tvComboTrafType, self).__init__(parent)

    self.clear()
    [ self.addItem(i) for i in self.items ]

  def __str__(self):
    return self.currentIndex()

class QTrafView(QtGui.QWidget):

  def __init__(self, parent=None):
    super(QTrafView, self).__init__(parent)
    vboxRoot = QtGui.QVBoxLayout(self)

    ## dates
    hboxDRange = QtGui.QHBoxLayout()
    hboxDRange.addWidget(QtGui.QLabel("Интервал дат", self))
    self.dateS = tvDateEdit(self)
    self.dateE = tvDateEdit(self)
    hboxDRange.addWidget(self.dateS)
    hboxDRange.addWidget(self.dateE)

    ## times
    hboxTRange = QtGui.QHBoxLayout()
    hboxTRange.addWidget(QtGui.QLabel("Интервал время", self))
    self.timeS = tvTimeEdit(self)
    self.timeE = tvTimeEdit(self)
    hboxTRange.addWidget(self.timeS)
    hboxTRange.addWidget(self.timeE)

    ## table
      # ::panel
    hboxTablePanel = QtGui.QHBoxLayout()
    hboxTablePanel.addWidget(QtGui.QLabel("Трафик", self))
    self.comboTrafType = tvComboTrafType(self)
    hboxTablePanel.addWidget(self.comboTrafType)
      #
    vboxTable = QtGui.QVBoxLayout()
    self.table = tvTable(self)
    vboxTable.addLayout(hboxTablePanel)
    vboxTable.addWidget(self.table)

    ##
    vboxRoot.addLayout(hboxDRange)
    vboxRoot.addLayout(hboxTRange)
    vboxRoot.addLayout(vboxTable)
    self.setLayout(vboxRoot)
    self.setWindowTitle("Обзор трафика")

    ## SIGNALs
    self.timeS.timeChanged.connect(self.__timeCheck)
    self.timeE.timeChanged.connect(self.__timeCheck)

  __lockQuery = False
  def __timeCheck(self):
    self.__lockQuery = self.timeS == self.timeE

