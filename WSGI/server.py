#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Server.py

"""

from wsgiref.simple_server import make_server
from WSGI.hello import application

httpd = make_server('', 8000, application)
print('Server HTTP on port 8000...')
httpd.serve_forever()
