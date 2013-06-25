#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2011-2013 by Florian Mounier, Kozea
# This file is part of pystil, licensed under a 3-clause BSD license.

from tornado.ioloop import IOLoop
from tornado.options import options, parse_command_line
from subprocess import call

import pystil
parse_command_line()

import pystil.routes
import pystil.charts
import pystil.websocket
from pystil.context import pystil

pystil.listen(options.port, xheaders=True)
if options.debug:
    try:
        call("wsreload --url 'http://l:1789/*'", shell=True)
    except:
        pass

IOLoop.instance().start()
