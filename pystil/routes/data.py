#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2011 by Florian Mounier, Kozea
# This file is part of pystil, licensed under a 3-clause BSD license.

from datetime import datetime, date
from time import mktime
from flask import jsonify
from threading import Lock
from multicorn.requests import CONTEXT as c
from pystil.corns import Visit
from pygeoip import GeoIP
from urlparse import urlparse
import re

IPV4RE = re.compile(r"(\d{1,3}(\.|$)){4}")
BROWSER_VERSION_NUMBERS = {
    'opera': 1,
    'safari': 1,
    'chrome': 1}


ipdb_lock = Lock()


def register_data_routes(app):
    """Defines data routes"""
    gip = GeoIP(app.config['geoipdb'])
    log = app.logger

    def on(site):
        return c.site.matches(".*" + site + ".*") if site != '*' else True

    @app.route('/<site>/visit_by_day.json')
    def visit_by_day(site):
        today = date.today()
        day_start = datetime(today.year, today.month, today.day)
        month_start = datetime(today.year, today.month, 1)
        if today.month == 12:
            year = today.year + 1
            month = 1
        else:
            year = today.year
            month = today.month + 1
        month_end = datetime(year, month, 1)

        page_hits = [(int(1000 * mktime(
            datetime.strptime(visit['key'], '%Y-%m-%d').timetuple())),
                          visit['count']) for visit in Visit.all
                  .filter(on(site))
                  .filter((month_start <= c.date) & (c.date < month_end))
                  .map({'day': c.date.str()[:10]})
                  .groupby(c.day, count=c.len())
                  .sort(c.key)
                  .execute()]

        new_visits = [(int(1000 * mktime(
            datetime.strptime(visit['key'], '%Y-%m-%d').timetuple())),
                          visit['count']) for visit in Visit.all
                  .filter(on(site))
                  .filter((month_start <= c.date) & (c.date < month_end))
                  .filter(c.last_visit == None)
                  .map({'day': c.date.str()[:10]})
                  .groupby(c.day, count=c.len())
                  .sort(c.key)
                  .execute()]
        visits = [(int(1000 * mktime(
            datetime.strptime(visit['key'], '%Y-%m-%d').timetuple())),
                          visit['count']) for visit in Visit.all
                  .filter(on(site))
                  .filter((c.last_visit == None) | (c.last_visit < day_start))
                  .filter((month_start <= c.date) & (c.date < month_end))
                  .map({'day': c.date.str()[:10]})
                  .groupby(c.day, count=c.len())
                  .sort(c.key)
                  .execute()]
        return jsonify({'series': [
            {'label': 'Page hits',
             'data': page_hits},
            {'label': 'Visits',
             'data': visits},
            {'label': 'New visits',
             'data': new_visits}]})

    @app.route('/<site>/visit_by_time.json')
    def visit_by_time(site):
        visits = [visit
                  for visit in Visit.all
                  .filter(on(site))
                  .map(c.time / 60000)
                  .groupby(c, count=c.len())
                  .execute() if visit is not None]
        return jsonify({'label': 'Time spent on site (in min)',
                        'data': visits,
                        'color': '#00FF00'})

    @app.route('/<site>/visit_by_hour.json')
    def visit_by_hour(site):
        visits = [(int(visit['key']), visit['count']) for visit in Visit.all
                  .filter(on(site))
                  .map({'hour': c.date.str()[11:13]})
                  .groupby(c.hour, count=c.len())
                  .sort(c.key)
                  .execute()]
        return jsonify({'label': 'Visits per hour', 'data': visits})

    @app.route('/<site>/visit_by_browser.json')
    def visit_by_browser(site):
        visits = [{'label': visit['key'],
                   'data': visit['count']} for visit in Visit.all
                  .filter(on(site))
                  .groupby(c.browser_name, count=c.len())
                  .sort(c.key)
                  .execute()]
        return jsonify({'list': visits})

    @app.route('/<site>/visit_by_browser_version.json')
    def visit_by_browser_version(site):
        visits = [{
            'label': '%s %s' % (
                visit['browser_name'], visit['browser_version']),
            'data': 1} for visit in Visit.all
                  .filter(on(site))
                  .execute()]

        version_visits = {}
        for visit in visits:
            label, data = visit['label'], visit['data']
            browser = label.split(' ')[0]
            if '.' in label:
                label = '.'.join(
                    label.split('.')[:BROWSER_VERSION_NUMBERS.get(browser, 2)])
            if label in version_visits:
                version_visits[label] += data
            else:
                version_visits[label] = data
        visits = [
            {'label': key, 'data': value}
            for key, value in version_visits.items()]
        return jsonify({'list': visits})

    @app.route('/<site>/visit_by_platform.json')
    def visit_by_platform(site):
        visits = [{'label': visit['key'],
                   'data': visit['count']} for visit in Visit.all
                  .filter(on(site))
                  .groupby(c.platform, count=c.len())
                  .sort(c.key)
                  .execute()]
        return jsonify({'list': visits})

    @app.route('/<site>/visit_by_resolution.json')
    def visit_by_resolution(site):
        visits = [{'label': visit['key'],
                   'data': visit['count']} for visit in Visit.all
                  .filter(on(site))
                  .groupby(c.size, count=c.len())
                  .sort(c.key)
                  .execute()]
        return jsonify({'list': visits})

    @app.route('/<site>/visit_by_referrer.json')
    def visit_by_referrer(site):
        full_referrers = [{'label': visit['key'],
                   'data': visit['count']} for visit in Visit.all
                  .filter(on(site))
                  .filter(c.referrer != None)
                  .groupby(c.referrer, count=c.len())
                  .sort(c.key)
                  .execute()]
        visits = {}
        for referrer in full_referrers:
            host = urlparse(referrer['label']).netloc.split(':')[0]
            visits[host] = visits.get(host, 0) + referrer['data']
        visits = [{'label': key,
                   'data': value} for key, value in visits.items()]
        return jsonify({'list': visits})

    @app.route('/<site>/visit_by_host.json')
    def visit_by_host(site):
        visits = [{'label': visit['key'],
                   'data': visit['count']} for visit in Visit.all
                  .filter(on(site))
                  .groupby(c.host, count=c.len())
                  .sort(c.key)
                  .execute()]
        return jsonify({'list': visits})

    @app.route('/<site>/visit_by_city.json')
    def visit_by_city(site):
        ips = (Visit.all
               .filter(on(site))
               .map(c.ip) .execute())
        visits = {}
        for ip in ips:
            # TODO Handle class B 172.16.0.0 -> 172.31.255.255
            ip = ip.replace('::ffff:', '')
            if IPV4RE.match(ip):
                if (ip == '127.0.0.1'
                    or ip.startswith('192.168.')
                    or ip.startswith('10.')):
                    city = 'Local'
                else:
                    with ipdb_lock:
                        location = gip.record_by_addr(ip)
                    city = (location.get('city', 'Unknown')
                            .decode('latin-1')
                            if location else 'Unknown')
            else:
                city = 'ipv6'
            visits[city] = visits.get(city, 0) + 1
        visits = [{'label': key,
                   'data': value} for key, value in visits.items()]
        return jsonify({'list': visits})

    @app.route('/<site>/visit_by_country.json')
    def visit_by_country(site):
        ips = (Visit.all
               .filter(on(site))
               .map(c.ip) .execute())
        visits = {}
        for ip in ips:
            # TODO Handle class B 172.16.0.0 -> 172.31.255.255
            ip = ip.replace('::ffff:', '')
            if IPV4RE.match(ip):
                if (ip == '127.0.0.1'
                    or ip.startswith('192.168.')
                    or ip.startswith('10.')):
                    country = 'Local'
                else:
                    with ipdb_lock:
                        location = gip.record_by_addr(ip)
                    country = (location.get('country_name', 'Unknown')
                            .decode('iso-8859-1')
                            if location else 'Unknown')
            else:
                country = 'ipv6'
            visits[country] = visits.get(country, 0) + 1
        visits = [{'label': key,
                   'data': value} for key, value in visits.items()]
        return jsonify({'list': visits})
