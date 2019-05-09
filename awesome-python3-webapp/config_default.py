#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
config_default.py

"""

configs = {
    'debug': True,
    'db': {
        'host': '127.0.0.1',
        'port': 3306,
        'user': 'www-data',
        'password': '1234',
        'db': 'awesome'
    },
    'session': {
        'secret': 'Awesome'
    }
}