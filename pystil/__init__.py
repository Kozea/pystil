#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2011 by Florian Mounier, Kozea
# This file is part of pystil, licensed under a 3-clause BSD license.
"""
pystil - An elegant site web traffic analyzer
"""
from flask import Flask
from logging import getLogger, INFO
from pystil.log import get_default_handler
from pystil.routes import register_common_routes
from pystil.routes.data import register_data_routes


def app():
    """Create Flask app"""
    app = Flask(__name__)
    handler = get_default_handler()
    getLogger('werkzeug').addHandler(handler)
    getLogger('werkzeug').setLevel(INFO)
    app.logger.handlers = []
    app.logger.addHandler(handler)
    register_common_routes(app)
    register_data_routes(app)
    return app
