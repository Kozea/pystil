# -*- coding: utf-8 -*-
# Copyright (C) 2011-2013 by Florian Mounier, Kozea
# This file is part of pystil, licensed under a 3-clause BSD license.

"""
pystil - An elegant site web traffic analyzer
"""

from tornado.options import define


define("port", default="1789", help="Pystil port")
define("db_host", default="localhost", help="Pystil db host")
define("db_name", default="pystil", help="Pystil db name")
define("db_user", default="pystil", help="Pystil db user")
define("db_password", default="pystil", help="Pystil db password")
define("db_port", default=5432, help="Pystil db port")
define("debug", default=True, help="Debug mode")

# Import for db init
import pystil.routes
import pystil.charts
import pystil.map
