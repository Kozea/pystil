#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2011 by Florian Mounier, Kozea
# This file is part of pystil, licensed under a 3-clause BSD license.

from datetime import datetime, date
from time import mktime
from flask import render_template, Response, request, send_file, jsonify
from multicorn.requests import CONTEXT as c
from uuid import uuid4
from pystil.corns import Visit
import csstyle


def register_common_routes(app):
    """Defines common routes"""
    log = app.logger

    @app.route('/')
    def index():
        """Nothing yet"""
        return render_template('index.jinja2')

    @app.route("/css.css")
    def css():
        """Render the css with some url_for in it"""
        text = render_template('css/css.jinja2')
        for browser in csstyle.BROWSERS:
            browser_parser = getattr(csstyle, browser)
            text += '\n\n/* CSS for %s */\n\n' % browser
            parser = csstyle.Parser(text=render_template('css/css.jinja2'))
            text += repr(browser_parser.transform(parser, keep_existant=False))
        return Response(text, mimetype='text/css')

    @app.route("/js.js")
    def js_():
        """Render the js with some url_for in it"""
        return Response(render_template('js/js.jinja2'),
                        mimetype='text/javascript')

    @app.route('/pystil-<int:stamp>-<string:kind>.gif')
    def pystil_gif(stamp, kind):
        """Fake gif get to bypass crossdomain problems."""
        gif = send_file('static/pystil.gif')
        uuid = request.args.get('_', None)
        if not uuid:
            log.warn("No uuid in request %r" % request)
            return gif
        if kind == 'o':
            visit = {}
            visit['uuid'] = uuid
            visit['site'] = request.args.get('u', None)
            visit['referrer'] = request.args.get('r', None)
            visit['size'] = request.args.get('s', None)
            visit['page'] = request.args.get('p', None)
            visit['hash'] = request.args.get('h', None)
            visit['query'] = request.args.get('q', None)
            visit['date'] = datetime.fromtimestamp(stamp / 1000.)
            visit['ip'] = request.remote_addr
            visit['browser_name'] = request.user_agent.browser
            visit['browser_version'] = request.user_agent.version
            visit['platform'] = request.user_agent.platform
            visit['language'] = request.user_agent.language
            visit = Visit.create(visit)
        elif kind == 'c':
            visit = Visit.all.filter(c.uuid == uuid).one().execute()
            visit['time'] = request.args.get('t', None)
        else:
            log.warn("No uuid in request %r" % request)
            return gif
        log.warn("Visit %r" % visit)
        visit.save()
        return gif

    @app.route('/pystil.js')
    def pystil_js():
        """Render the js with some jinja in it"""
        return Response(
            render_template('js.jinja2',
                            url_root=request.url_root, uuid=str(uuid4())),
            mimetype='text/javascript')
