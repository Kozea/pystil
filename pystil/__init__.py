#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2011 by Florian Mounier, Kozea
# This file is part of pystil, licensed under a 3-clause BSD license.
"""
pystil - An elegant visit tracker
"""

from flask import Flask, render_template, Response, request, send_file
from brigit.log import get_default_handler
from logging import getLogger, INFO
from datetime import datetime


APP = Flask(__name__)
HANDLER = get_default_handler()
getLogger('werkzeug').addHandler(HANDLER)
getLogger('werkzeug').setLevel(INFO)
APP.logger.handlers = []
APP.logger.addHandler(HANDLER)
# Temporary handle id as a global
ID = {'i': 0}


@APP.route('/')
def index():
    """Nothing yet"""
    return 'Hey'


@APP.route('/pystil-<int:stamp>-<string:kind>.gif')
def pystil_gif(stamp, kind):
    """Fake gif get to bypass crossdomain problems."""
    visit = {}
    visit['id'] = request.args.get('_', None)
    visit['debug'] = request.args.get('d', None)
    if kind == 'o':
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
    elif kind == 'c':
        visit['time'] = request.args.get('t', None)
    from pprint import pprint
    pprint(visit)
    return send_file('static/pystil.gif')


@APP.route('/pystil.js')
def pystil_js():
    """Render the js with some jinja in it"""
    ID['i'] += 1
    return Response(
        render_template('js.jinja2',
                        url_root=request.url_root, id=ID['i']),
        mimetype='text/javascript')


if __name__ == '__main__':
    APP.run(debug=True, threaded=True, host='0.0.0.0', port=12345)
