#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2011 by Florian Mounier, Kozea
# This file is part of pystil, licensed under a 3-clause BSD license.
"""
pystil - An elegant site web traffic analyzer
"""

import os
import sys
import pika
import gevent

ROOT = os.path.dirname(__file__)

from flask import Flask
from logging import getLogger, INFO, WARN, DEBUG, basicConfig
from log_colorizer import make_colored_stream_handler
from pystil.routes import register_common_routes
from pystil.routes.data import register_data_routes
from pystil.routes.admin import register_admin_routes
from pystil.routes.public import register_public_routes
from pystil.db import db
from gevent.event import Event


def app():
    """Create Flask app"""
    static_folder = os.path.join(ROOT, 'static')
    template_folder = os.path.join(ROOT, 'templates')
    from pystil import config

    if not config.FROZEN:
        print "Config MUST be frozen before pystil init"
        sys.exit(1)
    app = Flask(__name__,
                static_folder=static_folder,
                template_folder=template_folder)
    app.config.update(config.CONFIG)
    app.config['SQLALCHEMY_DATABASE_URI'] = config.CONFIG["DB_URL"]
    db.init_app(app)

    if app.config["LOG_FILE"]:
        basicConfig(filename=app.config["LOG_FILE"],
                            filemode='w', level=DEBUG)

    handler = make_colored_stream_handler()
    getLogger('werkzeug').addHandler(handler)
    getLogger('werkzeug').setLevel(INFO)
    getLogger('sqlalchemy').addHandler(handler)
    getLogger('sqlalchemy').setLevel(WARN)

    app.logger.handlers = []
    app.logger.addHandler(handler)

    if (not app.config.get("DEBUG", True) and
        app.config.get("LDAP_HOST", False) and
        app.config.get("LDAP_PATH", False)):
        from pystil.ldap_ import auth_route
        route = auth_route(app)
    else:
        route = app.route

    event = app.event = Event()
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='pystil')
    channel.exchange_declare(exchange='pystil', type='fanout')
    channel.queue_bind(exchange='pystil', queue='pystil')

    def callback(ch, method, properties, body):
        print "A" * 1000
        event.set()
        event.clear()
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(callback, queue='pystil')
    # Is it good or awful ?
    gevent.spawn(channel.start_consuming)

    register_data_routes(app, route)
    register_common_routes(app, route)
    register_admin_routes(app, route)
    return app
