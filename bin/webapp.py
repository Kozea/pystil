#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2011 by Florian Mounier, Kozea
# This file is part of pystil, licensed under a 3-clause BSD license.
"""
pystil - An elegant site web traffic analyzer
"""

import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
pystil_parent_path = os.path.abspath(current_dir + "/..")
if pystil_parent_path not in sys.path:
    sys.path.append(pystil_parent_path)

from pystil import app, config
import werkzeug.contrib.fixers
config.freeze()

from pystil.service.http import Application
from gevent import monkey
monkey.patch_all()
import gevent.wsgi
application = werkzeug.contrib.fixers.ProxyFix(Application(app()))
ws = gevent.wsgi.WSGIServer(('', 1789), application)
ws.serve_forever()
