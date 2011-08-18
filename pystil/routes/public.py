#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2011 by Florian Mounier, Kozea
# This file is part of pystil, licensed under a 3-clause BSD license.

from flask import Response, request, send_file
from ..service.data import Message
from ..service.http import render_js


def register_public_routes(app):
    """Defines public routes"""

    @app.route('/pystil-<int:stamp>.gif')
    def pystil_gif(stamp):
        """Fake gif get to bypass crossdomain problems."""
        gif = send_file('static/pystil.gif')
        message = Message(request.environ['QUERY_STRING'],
                request.environ['HTTP_USER_AGENT'],
                request.environ['REMOTE_ADDR'])
        message.process()
        return gif

    @app.route('/pystil.js')
    def pystil_js():
        """Render the js with some jinja in it"""
        return Response(
                render_js(request.environ),
                mimetype='text/javascript')
