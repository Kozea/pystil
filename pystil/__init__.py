#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2011 by Florian Mounier, Kozea
# This file is part of pystil, licensed under a 3-clause BSD license.
"""
pystil - An elegant site web traffic analyzer
"""

import os
import sys

ROOT = os.path.dirname(__file__)

import logging
from flask import Flask
from logging import getLogger, INFO

from pystil.log import get_default_handler
from pystil.routes import register_common_routes
from pystil.routes.data import register_data_routes
from pystil.routes.public import register_public_routes

def app():
    """Create Flask app"""
    static_folder = os.path.join(ROOT, 'static')
    template_folder = os.path.join(ROOT, 'templates')
    app = Flask(__name__,
                static_folder=static_folder,
                template_folder=template_folder)

    from pystil import config
    if not config.FROZEN:
        print "Config MUST be frozen before pystil init"
        sys.exit(1)

    app.config.update(config.CONFIG)
    if app.config["LOG_FILE"]:
        logging.basicConfig(filename=app.config["LOG_FILE"],
                            filemode='w', level=logging.DEBUG)

    handler = get_default_handler()
    getLogger('werkzeug').addHandler(handler)
    getLogger('werkzeug').setLevel(INFO)

    app.logger.handlers = []
    app.logger.addHandler(handler)

    if (app.config.get("LDAP_HOST", False) and
        app.config.get("LDAP_PATH", False)):
        from pystil.ldap_ import auth_route
        route = auth_route(app)
    else:
        route = app.route

    if app.config.get("PUBLIC_ROUTES", True):
        register_public_routes(app)

    register_data_routes(app, route)
    register_common_routes(app, route)
    return app
