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

import logging

import sqlite3


class Storage(object):

  def __init__(self, opt):
    pass

  def createdb(self):
    """Create or erase database."""
    raise NotImplemented()

  def date_is_fixed(self, date):
    """Check if all data for specified date is cached and fixed."""
    raise NotImplemented()

  def update_data(self, data):
    """Update database with specified data."""
    raise NotImplemented()

  def fix_date(self, date):
    """Mark cached data for specified date as fixed."""
    raise NotImplemented()

  def get_amounts(self, contrid, date, hours):
    """Return cached traffic amounts for specified date split and specified hours."""
    raise NotImplemented()


class SqliteStorage(Storage):

  def __init__(self, opt):
    self.dbname = os.path.join(opt.workdir, 'sqlite.db')
    if not os.path.exists(self.dbname):
      self.create_db()
    self.db = sqlite3.connect(self.dbname)

  def createdb(self):

    with sqlite3.connect(self.dbname) as conn:
      c = conn.cursor()
      c.executescript("""
create table amounts_in (
    contrid integer,
    date char(8),
    hour integer,
    amount bigint,
    primary key(contrid, date, hour)
);

create table amounts_out (
    contrid integer,
    date char(8),
    hour integer,
    amount bigint,
    primary key(contrid, date, hour)
);

create table fixeddays (
    date char(8)
);
            """)

  def date_is_fixed(self, date):
    """Check if all data for specified date is cached and fixed."""
    with self.db.cursor() as c:
      c.

  def update_data(self, data):
    """Update database with specified data."""
    raise NotImplemented()

  def fix_date(self, date):
    """Mark cached data for specified date as fixed."""
    raise NotImplemented()

  def get_amounts(self, contrid, date, hours):
    """Return cached traffic amounts for specified date split and specified hours."""
    raise NotImplemented()


# vim: set ts=2 sw=2:
