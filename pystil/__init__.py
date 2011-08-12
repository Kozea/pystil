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
import pystil
import os


def app():
    """Create Flask app"""
    root = os.path.dirname(pystil.__file__)
    static_folder = os.path.join(root, 'static')
    template_folder = os.path.join(root, 'templates')
    app = Flask(__name__,
                static_folder=static_folder, template_folder=template_folder)
    handler = get_default_handler()
    getLogger('werkzeug').addHandler(handler)
    getLogger('werkzeug').setLevel(INFO)
    app.logger.handlers = []
    app.logger.addHandler(handler)
    register_common_routes(app)
    register_data_routes(app)
    return app
