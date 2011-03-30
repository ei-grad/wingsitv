#!/usr/bin/env python3
# coding: utf-8

import os
from configparser import RawConfigParser


DEFAULT_WORKDIR = os.path.expanduser(os.path.join('~', '.wingsitv'))

config = RawConfigParser()
configfile = os.path.join(DEFAULT_WORKDIR, 'config.ini')

def save_config():
    with open(configfile, 'w') as f: config.write(f)

if os.path.exists(configfile):
      config.read(configfile)

if 'chat' not in config:
    config['chat'] = {
            'login': None,
            'show': True
        }

if 'utm5' not in config:
    config['utm5'] = {
            'login': None,
            'passwd': None,
            'show': None,
            'url': 'https://mnx.net.ru/utm5',
            'hours': '01-10'
        }

