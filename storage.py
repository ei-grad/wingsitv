#!/usr/bin/env python3
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


__all__ = [ 'storage' ]

import os
import sys

from utm5client import logging

import sqlite3


class Storage(object):

  def __init__ (self, opt):

    self.backend = opt.db_backend
    self.hours = opt.hours

    if self.backend = 'sqlite':

      self.dbname = os.join(opt.workdir, 'sqlite.db')
      if not os.path.exists(self.dbname):
        self._sqlite_createdb()
      self.db = sqlite3.connect(self.dbname)

    elif self.backend = 'plaintext':
      self.dbname = os.join(opt.workdir, 'data.txt')
      if not os.path.exists(self.dbname):
        self._plain_createdb()

    else:
      raise Exception('unknown storage backend')

  def _plain_update_data(self, date):
    raise NotImplemented()

  def _plain_get_amounts(self, date):
    raise NotImplemented()

  def _plain_date_is_fixed(self, date):
    raise NotImplemented()

  def _plain_createdb(self):
    raise NotImplemented()

  def _sqlite_update_data(self, date):
    raise NotImplemented()

  def _sqlite_get_amounts(self, date):
    raise NotImplemented()

  def _sqlite_date_is_fixed(self, date):
    raise NotImplemented()

  def _sqlite_createdb(self):

    with sqlite3.connect(self.dbname) as conn:
      c = conn.cursor()
      c.executescript("""
create table in (
    contrid integer,
    date char(8),
    time char(8),
    amount bigint,
    primary key(contrid, date, time)
);

create table out (
    contrid integer,
    date char(8),
    time char(8),
    amount bigint,
    primary key(contrid, date, time)
)

create index contrid_idx on in (contrid);
create index contrid_idx on out (contrid);

create table fixeddays (
    date char(8)
)
            """)


# vim: set ts=2 sw=2:
