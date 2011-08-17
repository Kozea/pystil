#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2011 by Florian Mounier, Kozea
# This file is part of pystil, licensed under a 3-clause BSD license.

from datetime import datetime
from flask import render_template, Response, request, send_file
from multicorn.requests import CONTEXT as c
from pygeoip import GeoIP, MMAP_CACHE
from threading import Lock
from uuid import uuid4
import re


def register_public_routes(app):
    """Defines public routes"""
    from pystil.corns import Visit
    log = app.logger
    gip = GeoIP(app.config['IP_DB'], MMAP_CACHE)
    geoip_db_lock = Lock()
    ipv4re = re.compile(r"(\d{1,3}(\.|$)){4}")

    def add_geolocalization(ip, visit):
        lat = None
        lng = None
        ip = ip.replace('::ffff:', '')
        if ipv4re.match(ip):
            if (ip == '127.0.0.1'
                or ip.startswith('192.168.')
                or ip.startswith('10.')):
                city = 'Local'
                country = 'Local'
            else:
                with geoip_db_lock:
                    location = gip.record_by_addr(ip)
                city = (location.get('city', 'Unknown')
                        .decode('iso-8859-1')
                        if location else 'Unknown')
                country = (location.get('country_name', 'Unknown')
                        .decode('iso-8859-1')
                        if location else 'Unknown')
                lat = location.get('latitude', None)
                lng = location.get('longitude', None)
        else:
            country = 'ipv6'
            city = 'ipv6'
        visit['country'] = country
        visit['city'] = city
        visit['lat'] = lat
        visit['lng'] = lng

    @app.route('/pystil-<int:stamp>.gif')
    def pystil_gif(stamp):
        """Fake gif get to bypass crossdomain problems."""
        gif = send_file('static/pystil.gif')
        uuid = request.args.get('_', None)
        if not uuid:
            log.warn("No uuid in request %r" % request)
            return gif
        kind = request.args.get('d', None)
        if kind == 'o':
            last_visit = request.args.get('l', None)
            if last_visit:
                last_visit = datetime.fromtimestamp(int(last_visit) / 1000)
            visit = {}
            visit['uuid'] = uuid
            visit['host'] = request.args.get('k', None)
            visit['site'] = request.args.get('u', None)
            visit['client_tz_offset'] = request.args.get('z', 0)
            visit['date'] = datetime.now()
            visit['last_visit'] = last_visit
            visit['referrer'] = request.args.get('r', None)
            visit['size'] = request.args.get('s', None)
            visit['page'] = request.args.get('p', None)
            visit['hash'] = request.args.get('h', None)
            visit['query'] = request.args.get('q', None)
            visit['browser_name'] = request.user_agent.browser
            visit['browser_version'] = request.user_agent.version
            visit['platform'] = request.user_agent.platform
            visit['language'] = request.user_agent.language
            ip = request.remote_addr
            visit['ip'] = ip
            add_geolocalization(ip, visit)
            visit = Visit.create(visit)
        elif kind == 'c':
            visit = next(
                Visit.all.filter(c.uuid == uuid).sort(-c.date).execute(), None)
            if visit:
                visit['time'] = request.args.get('t', None)
        else:
            log.warn("No uuid in request %r" % request)
            return gif
        log.debug("Visit %r" % visit.items())
        visit.save()
        return gif

    @app.route('/pystil.js')
    def pystil_js():
        """Render the js with some jinja in it"""
        return Response(
            render_template('js/pystil.jinja2',
                            url_root=request.url_root, uuid=str(uuid4())),
            mimetype='text/javascript')
