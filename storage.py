#!/usr/bin/env python3
# coding: utf-8

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
