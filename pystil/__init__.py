#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2011 by Florian Mounier, Kozea
# This file is part of pystil, licensed under a 3-clause BSD license.
"""
pystil - An elegant site web traffic analyzer
"""

from brigit.log import get_default_handler
from datetime import datetime, date
from time import mktime
from flask import Flask, render_template, Response, request, send_file, jsonify
from logging import getLogger, INFO
from multicorn import Multicorn
from multicorn.corns.alchemy import Alchemy
from multicorn.declarative import declare, Property
from multicorn.requests import CONTEXT as c
from uuid import uuid4
import csstyle
MC = Multicorn()


@MC.register
@declare(Alchemy, identity_properties=['uuid'], url='sqlite:///pystil.db')
class Visit(object):
    """This corn contains the visits"""
    uuid = Property()
    browser_name = Property()
    browser_version = Property()
    date = Property(type=datetime)
    hash = Property()
    ip = Property()
    language = Property()
    page = Property()
    platform = Property()
    query = Property()
    referrer = Property()
    site = Property()
    size = Property()
    time = Property(type=int)


APP = Flask(__name__)
HANDLER = get_default_handler()
getLogger('werkzeug').addHandler(HANDLER)
getLogger('werkzeug').setLevel(INFO)
APP.logger.handlers = []
APP.logger.addHandler(HANDLER)


@APP.route('/')
def index():
    """Nothing yet"""
    return render_template('index.jinja2')


@APP.route('/visit_by_day.json')
def visit_by_day():
    today = date.today()
    month_start = datetime(today.year, today.month, 1)
    if today.month == 12:
        year = today.year + 1
        month = 1
    else:
        year = today.year
        month = today.month + 1
    month_end = datetime(year, month, 1)

    visits = [(int(1000 * mktime(
        datetime.strptime(visit['key'], '%Y-%m-%d').timetuple())),
                      visit['count']) for visit in Visit.all
              .filter((month_start <= c.date) & (c.date < month_end))
              .map({'day': c.date.str()[:10]})
              .groupby(c.day, count=c.len())
              .sort(c.key)
              .execute()]
    return jsonify({'label': 'Visits per day',
                    'data': visits, 'color': '#FF00FF'})


@APP.route('/visit_by_hour.json')
def visit_by_hour():
    visits = [(int(visit['key']), visit['count']) for visit in Visit.all
              .map({'hour': c.date.str()[11:13]})
              .groupby(c.hour, count=c.len())
              .sort(c.key)
              .execute()]
    return jsonify({'label': 'Visits per hour', 'data': visits})


@APP.route('/visit_by_browser.json')
def visit_by_browser():
    visits = [{'label': visit['key'],
               'data': visit['count']} for visit in Visit.all
              .groupby(c.browser_name, count=c.len())
              .sort(c.key)
              .execute()]
    return jsonify({'list': visits})


@APP.route("/css.css")
def css():
    """Render the css with some url_for in it"""
    text = render_template('css/css.jinja2')
    for browser in csstyle.BROWSERS:
        browser_parser = getattr(csstyle, browser)
        text += '\n\n/* CSS for %s */\n\n' % browser
        parser = csstyle.Parser(text=render_template('css/css.jinja2'))
        text += repr(browser_parser.transform(parser, keep_existant=False))
    return Response(text, mimetype='text/css')


@APP.route("/js.js")
def js_():
    """Render the js with some url_for in it"""
    return Response(render_template('js/js.jinja2'),
                    mimetype='text/javascript')


@APP.route('/pystil-<int:stamp>-<string:kind>.gif')
def pystil_gif(stamp, kind):
    """Fake gif get to bypass crossdomain problems."""
    gif = send_file('static/pystil.gif')
    uuid = request.args.get('_', None)
    if not uuid:
        APP.logger.warn("No uuid in request %r" % request)
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
        APP.logger.warn("No uuid in request %r" % request)
        return gif
    APP.logger.warn("Visit %r" % visit)
    visit.save()
    return gif


@APP.route('/pystil.js')
def pystil_js():
    """Render the js with some jinja in it"""
    return Response(
        render_template('js.jinja2',
                        url_root=request.url_root, uuid=str(uuid4())),
        mimetype='text/javascript')


if __name__ == '__main__':
    APP.run(debug=True, threaded=True, host='0.0.0.0', port=12345)
