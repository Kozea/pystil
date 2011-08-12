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
import logging
import pystil
import os


def app(ipdb='ip.db', log=''):
    """Create Flask app"""
    if log:
        logging.basicConfig(filename=log, filemode='w', level=logging.DEBUG)
    root = os.path.dirname(pystil.__file__)
    static_folder = os.path.join(root, 'static')
    template_folder = os.path.join(root, 'templates')
    app = Flask(__name__,
                static_folder=static_folder,
                template_folder=template_folder)
    app.config['geoipdb'] = ipdb
    handler = get_default_handler()
    getLogger('werkzeug').addHandler(handler)
    getLogger('werkzeug').setLevel(INFO)
    app.logger.handlers = []
    app.logger.addHandler(handler)
    register_common_routes(app)
    register_data_routes(app)
    return app
