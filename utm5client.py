#! /usr/bin/env python3
#
#   Copyright (c) 2010-2011, Andrew Grigorev <andrew@ei-grad.ru>
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
from datetime import date
from getpass import getpass
import datetime

import logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(funcName)s: %(message)s")

from storage import Storage

select_contract = lambda contracts: list(contracts)[0]

class UTM5Client(object):

  traffic_re = re.compile(r'<TR><TD BGCOLOR=#B0B0B0>\d+<TD ALIGN=LEFT>&nbsp;(?P<date>\d\d\.\d\d\.\d\d)( (?P<time>\d\d:\d\d:\d\d)|)&nbsp;<TD ALIGN=LEFT>&nbsp;(?P<login>\w+)&nbsp;<TD ALIGN=CENTER>&nbsp;(?P<direction>[<>])&nbsp;<TD ALIGN=LEFT>&nbsp;(?P<traffic_type>[\w ]+)'
      '&nbsp;<TD ALIGN=CENTER>&nbsp;(?P<amount>\d+)&nbsp;')
  contracts_re = re.compile(r'''<A HREF="\?FORMNAME=IP_CONTRACT_INFO&SID=(?P<sid>\w+)&CONTR_ID=(?P<id>\d+)&NLS=WR" TITLE="Посмотреть данные по договору" target="_self" method="post">(?P<name>\w+)</A>
&nbsp;<TD ALIGN=CENTER>&nbsp;(?P<client>[\w ]+)&nbsp;<TD ALIGN=RIGHT>&nbsp;\d+.\d\d&nbsp;<TD ALIGN=RIGHT>&nbsp;\d+.\d\d&nbsp;''', re.MULTILINE)

  def __init__(self, opt):
    self.url = opt.url.strip('/')

    if opt.backend == 'sqlite':
      self.db = SqliteStorage(opt)

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

  def set_contract(self, contrid):
    self.sid = self.contracts[str(contrid)]['sid']
    self.contractid = contrid

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

    logging.info('Requesting {0} from UTM5'.format(date.isoformat()))

    month = '%.2d.%d' % (date.month, date.year)
    day = date.day

    res = urlopen(self.url+'/!w3_p_main.showform',
      data=urlencode({
                'CONTRACTID': self.contractid,
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
      amount = e.group('amount')
      time = e.group('time') or '00:00:00'
      date = e.group('date')
      data.append((date, time, direction, amount))

    return data

  def get_month_traffic(self, year=date.today().year, month=date.today().month, traffic_type="LLTRAF_INET"):

    date = datetime.date(year, month, 1)

    if date > date.today():
      raise Exception(date.strftime("Нельзя узнать свою статистику за %B %Y"))

    amounts = [0]*4

    while date.month == month:

      if not self.db.date_is_fixed(contrid, date):
        data = self.request_day_from_utm5(date)
        self.db.update_data(self.contrid, data)
        if date != datetime.today():
          self.db.fix_date(date)

      date_amounts = self.db.get_amounts(self.contrid, date)
      for i in range(4):
        amounts[i] += date_amounts[i]

      if date == datetime.today():
        break
      else:
        date += timedelta(days=1)

    return amounts


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
      default=os.path.expanduser(os.path.join('~', '.utm5client')))
  parser.add_option('-l', '--login', dest='login', metavar='LOGIN',
      help='логин от личного кабинета',
      default=None)
  parser.add_option('-p', '--passw', dest='passwd', metavar='PASSWORD',
      help='пароль от личного кабинета',
      default=None)
  parser.add_option('-n', '--night', dest='hours', metavar='N-M',
      help='ночное время (по умолчанию: %default)',
      default='01-10')
  parser.add_option('-r', '--refresh', dest='delay', metavar='DELAY',
      help='интервал обновления информации',
      default=300)
  parser.add_option('-b', '--backend', dest='backend', metavar='',
      help='бэкэнд хранения данных, sqlite или plaintext',
      default='sqlite3')
  opt, args = parser.parse_args()

  if opt.login is None:
    opt.login = input('Login:')

  if opt.passwd is None:
    opt.passwd = getpass('Password:')

  begin, end = [ int(i) for i in opt.hours.split('-') ]

  if begin < end:
    opt.night = list(range(begin, end))
  else:
    opt.night = list(range(0, end) + range(begin, 24))

  client = UTM5Client(opt)

  if not os.path.exists(opt.workdir):
    os.mkdir(opt.workdir)

  client.auth(opt.login, opt.passwd)
  sys.stdout.write(str(client.get_month_traffic()))

# vim: set ts=2 sw=2:
