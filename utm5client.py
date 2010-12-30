#! /usr/bin/env python3
#
#   Copyright (c) 2010-2011, Andrew Grigorev <andrew@ei-grad.ru>
#   Copyright (c) 2010-2011, Valentin Novikov <thelannor.beless@gmail.com>
#
#   All rights reserved.
#
#   Redistribution and use in source and binary forms, with or without
#   modification, are permitted provided that the following conditions are
#   met:
#
#       Redistributions of source code must retain the above copyright notice,
#       this list of conditions and the following disclaimer.  Redistributions
#       in binary form must reproduce the above copyright notice, this list of
#       conditions and the following disclaimer in the documentation and/or
#       other materials provided with the distribution.  Neither the name of
#       the <ORGANIZATION> nor the names of its contributors may be used to
#       endorse or promote products derived from this software without
#       specific prior written permission.
#
#   THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
#   IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
#   THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
#   PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
#   CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
#   EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
#   PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
#   PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
#   LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
#   NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
#   SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#


__all__ = [ 'UTM5Client' ]

import re, sys, os, atexit, getpass
from urllib.request import urlopen
from urllib.parse import urlencode
from datetime import datetime, timedelta
from getpass import getpass
import logging
import sqlite3


DEFAULT_WORKDIR = os.path.expanduser(os.path.join('~', '.utm5client'))

class Storage(object):

  def __init__(self, workdir=DEFAULT_WORKDIR):
    self.dbname = os.path.join(workdir, 'sqlite.db')
    if not os.path.exists(self.dbname):
      self.create_db()
    self.db = sqlite3.connect(self.dbname)

  def create_db(self):
    with sqlite3.connect(self.dbname) as conn:
      conn.executescript("""
create table amounts_in (
    cid integer,
    date char(8),
    hour integer,
    amount bigint,
    primary key(cid, date, hour)
);

create table amounts_out (
    cid integer,
    date char(8),
    hour integer,
    amount bigint,
    primary key(cid, date, hour)
);

create table fixeddays (
    cid integer,
    date char(8),
    primary key(cid, date)
);
            """)

  def date_is_fixed(self, cid, date):
    """Check if all data for specified date is cached and fixed."""
    date = date.strftime('%d.%m.%y')
    with self.db:
      c = self.db.cursor()
      c.execute("select count(*) from fixeddays where cid = ? and date = ?", (cid, date))
      return c.fetchone()[0] == 1

  def update_data(self, cid, data):
    """Update database with specified data."""
    with self.db:
        self.db.executemany('insert or replace into amounts_in values (?, ?, ?, ?)', [
            (cid, d[1], d[2], d[3]) for d in data if d[0] == 'in'
          ])
        self.db.executemany('insert or replace into amounts_out values (?, ?, ?, ?)', [
            (cid, d[1], d[2], d[3]) for d in data if d[0] == 'out'
          ])

  def fix_date(self, cid, date):
    """Mark cached data for specified date as fixed."""
    date = date.strftime('%d.%m.%y')
    with self.db:
      self.db.execute('insert or ignore into fixeddays values (?, ?)', (cid, date))

  def get_amounts(self, cid, date, hours):
    """Return cached traffic amounts for specified date split and specified hours."""
    date = date.strftime('%d.%m.%y')
    with self.db:
      c = self.db.cursor()
      c.execute('select sum(amount) from amounts_in where cid = ? and date = ? and hour in (' + ','.join(['?'] * len(hours)) +')', (cid, date) + tuple(hours))
      sum_in = c.fetchone()[0] or 0
      c.close()
      c = self.db.cursor()
      c.execute('select sum(amount) from amounts_out where cid = ? and date = ? and hour in (' + ','.join(['?'] * len(hours)) + ')', (cid, date) + tuple(hours))
      sum_out = c.fetchone()[0] or 0
      c.close()

    return sum_in, sum_out


class UTM5Client(object):

  traffic_re = re.compile(r'<TR><TD BGCOLOR=#B0B0B0>\d+<TD ALIGN=LEFT>&nbsp;(?P<date>\d\d\.\d\d\.\d\d)( (?P<time>\d\d:\d\d:\d\d)|)&nbsp;<TD ALIGN=LEFT>&nbsp;(?P<login>\w+)&nbsp;<TD ALIGN=CENTER>&nbsp;(?P<direction>[<>])&nbsp;<TD ALIGN=LEFT>&nbsp;(?P<traffic_type>[\w ]+)'
      '&nbsp;<TD ALIGN=CENTER>&nbsp;(?P<amount>\d+)&nbsp;')
  contracts_re = re.compile(r'''<A HREF="\?FORMNAME=IP_CONTRACT_INFO&SID=(?P<sid>\w+)&CONTR_ID=(?P<id>\d+)&NLS=WR" TITLE="Посмотреть данные по договору" target="_self" method="post">(?P<name>\w+)</A>
&nbsp;<TD ALIGN=CENTER>&nbsp;(?P<client>[\w ]+)&nbsp;<TD ALIGN=RIGHT>&nbsp;\d+.\d\d&nbsp;<TD ALIGN=RIGHT>&nbsp;\d+.\d\d&nbsp;''', re.MULTILINE)

  def __init__(self, url, hours, workdir=DEFAULT_WORKDIR):
    self.url = url.strip('/')
    self.hours = hours
    self.db = Storage(workdir)

  def auth(self, login, passwd):
    """
      Authenticates and retrieves a list of available contracts.
    """
    logging.info('Authenticating as {0}...'.format(login))
    res = urlopen(self.url+'/!w3_p_main.showform',
      data=urlencode({'SID': '',
                    'NLS': 'WR',
                    'USERNAME': login,
                    'PASSWORD': passwd,
                    'FORMNAME': 'IP_CONTRACTS',
                    'BUTTON': 'Вход'.encode('cp1251')
                    })).read().decode('cp1251')

    self.contracts = {c.group('id'): c.groupdict() for c in self.contracts_re.finditer(res)}

    if not self.contracts:
      logging.error('Authentication failed! No contracts!')
      raise Exception('Authentication failed! No contracts!')

    self.set_contract(list(self.contracts)[0])

  def set_contract(self, cid):
    self.sid = self.contracts[str(cid)]['sid']
    self.cid = cid

  def request_day_from_utm5(self, date, traffic_type="LLTRAF_INET"):
    """
      Get info from UTM5 client area by HTTP.

      @param month: month in form "MM.YYYY"
      @param day: day of month
      @param traffic_type: type of traffic
            LLTRAF_INET - internet (default)
            LLTRAF_MM - multimedia
            LLTRAF_LOC - local
    """

    logging.info('Requesting %d.%d.%d from UTM5' % date.timetuple()[:3])

    month = '%.2d.%d' % (date.month, date.year)
    day = date.day

    res = urlopen(self.url+'/!w3_p_main.showform',
      data=urlencode({
                'CONTRACTID': self.cid,
                "DIR": "",
                "SRV": traffic_type,
                "MONTH": month,
                "DAY": day,
                "UNITS_VIEW": "1",
                "SID": self.sid,
                "NLS": "WR",
                "FORMNAME": "LL_TRAFFIC2",
                "BUTTON": 'Показать'.encode('cp1251')
               })).read().decode('cp1251')

    data = []

    for e in self.traffic_re.finditer(res):
      direction = "in" if e.group('direction') == "<" else "out"
      date = e.group('date')
      time = int((e.group('time') or '00:00:00')[:2])
      amount = e.group('amount')
      data.append((direction, date, time, amount))

    return data

  def get_month_traffic(self, year=datetime.today().year, month=datetime.today().month, traffic_type="LLTRAF_INET"):

    today = datetime.today().date()
    date = datetime(year, month, 1).date()

    if date > today:
      raise Exception(date.strftime("Нельзя узнать свою статистику за %B %Y"))

    daytime_amounts = [0, 0]
    full_amounts = [0, 0]

    while date.month == month:

      if not self.db.date_is_fixed(self.cid, date):
        data = self.request_day_from_utm5(date)
        self.db.update_data(self.cid, data)
        if date != today:
          self.db.fix_date(self.cid, date)

      date_daytime_amounts = self.db.get_amounts(self.cid, date, self.hours)
      daytime_amounts[0] += date_daytime_amounts[0]
      daytime_amounts[1] += date_daytime_amounts[1]

      date_full_amounts = self.db.get_amounts(self.cid, date, list(range(24)))
      full_amounts[0] += date_full_amounts[0]
      full_amounts[1] += date_full_amounts[1]

      if date == today:
        break
      else:
        date += timedelta(days=1)

    return daytime_amounts, full_amounts


if __name__ == '__main__':
  from optparse import OptionParser
  parser = OptionParser(usage='Usage: %prog [options]', version='0.1.1')
  parser.add_option('-u', '--url', dest='url',
      help='адрес системы UTM5',
      default='https://mnx.net.ru/utm5')
  parser.add_option('-d', '--debug', action='store_true', dest='debug',
      help='вывод отладочных сообщений',
      default=False)
  parser.add_option('-v', '--verbose', action='store_true', dest='verbose',
      help='подробный вывод сообщений',
      default=False)
  parser.add_option('-w', '--workdir', dest='workdir',
      help='рабочая директория программы',
      default=DEFAULT_WORKDIR)
  parser.add_option('-l', '--login', dest='login', metavar='LOGIN',
      help='логин от личного кабинета',
      default=None)
  parser.add_option('-p', '--passw', dest='passwd', metavar='PASSWORD',
      help='пароль от личного кабинета',
      default=None)
  parser.add_option('-n', '--night', dest='night', metavar='N-M',
      help='ночное время (по умолчанию: %default)',
      default='01-10')
  opt, args = parser.parse_args()

  if opt.debug:
    logging.basicConfig(level=logging.DEBUG, format="%(message)s")
  elif opt.verbose:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
  else:
    logging.basicConfig(level=logging.WARNING, format="%(message)s")

  if opt.login is None:
    opt.login = input('Login: ')

  if opt.passwd is None:
    opt.passwd = getpass()

  begin, end = [ int(i) for i in opt.night.split('-') ]

  if begin < end:
    night_hours = list(range(begin, end))
  else:
    night_hours = list(range(0, end) + range(begin, 24))

  dayhours = list(set(range(24)) - set(night_hours))

  if not os.path.exists(opt.workdir):
    os.mkdir(opt.workdir)

  client = UTM5Client(opt.url, dayhours, opt.workdir)
  client.auth(opt.login, opt.passwd)
  daytime, full = client.get_month_traffic()

  def hum(size):
    SUFFIXES = ['KB', 'MB', 'GB']

    suf = 'B'

    for suffix in SUFFIXES:
      if size < 1024:
        break
      else:
        size /= 1024
        suf = suffix

    return '%.2f%s' % (size, suf)

  sys.stdout.write("\n")
  sys.stdout.write("= In =\nDaytime: %s\nFull: %s\n\n" % (hum(daytime[0]), hum(full[0])))
  sys.stdout.write("= Out =\nDaytime: %s\nFull: %s\n\n" % (hum(daytime[1]), hum(full[1])))

# vim: set ts=2 sw=2:
