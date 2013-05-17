# -*- coding: utf-8 -*-
# Copyright (C) 2011-2013 by Florian Mounier, Kozea
# This file is part of pystil, licensed under a 3-clause BSD license.

from pystil.utils import (
    try_decode, parse_ua, parse_referrer, parse_domain)
from pystil.db import Visit, country, city, asn
from datetime import datetime, timedelta
from sqlalchemy import desc


class Message(object):
    def __init__(self, log, qs_args, ua, ip):
        self.log = log
        self.qs_args = qs_args
        self.ua = ua
        self.stamp = datetime.utcnow()
        if ', ' in ip:
            self.ip = ip.split(', ')[0]
        else:
            self.ip = ip

    def process(self, db):
        self.log.info('Processing message %r' % self)

        def get(key, default=None, from_encoding=None):
            value = self.qs_args.get(key, [default])[0]
            if value and value == b'undefined':
                value = None
            if value is not None:
                if from_encoding:
                    value = value.decode(from_encoding)
                else:
                    value = try_decode(value)
            return value

        visit = None
        kind = get('d')
        uuid = get('_')
        platform, browser, version = parse_ua(self.ua)
        if kind == 'c':
            visit = (db
                     .query(Visit)
                     .filter(Visit.uuid == uuid)
                     .order_by(desc(Visit.date))
                     .first())
            if visit:
                visit.time = timedelta(seconds=int(get('t', 0)) / 1000)

        elif kind == 'o':
            last_visit = get('l')
            if last_visit and 'undefined' not in last_visit:
                last_visit = datetime.fromtimestamp(int(last_visit) / 1000)
            else:
                last_visit = None

            visit = {'uuid': uuid,
                     'host': get('k'),
                     'site': get('u'),
                     'client_tz_offset': int(float(get('z', 0))),
                     'date': self.stamp,
                     'last_visit': last_visit,
                     'ip': self.ip,
                     'referrer': get('r'),
                     'pretty_referrer': parse_referrer(
                         get('r', from_encoding='latin-1')),
                     'referrer_domain': parse_domain(
                         get('r', from_encoding='latin-1')),
                     'size': get('s'),
                     'page': get('p', from_encoding='latin-1'),
                     'hash': get('h', from_encoding='latin-1'),
                     'query_string': get('q'),
                     'language': get('i'),
                     'browser_name': browser,
                     'browser_version': version,
                     'platform': platform}

            lat = None
            lng = None
            city_name = None
            country_code = None
            country_name = None
            asn_name = None

            if self.ip.startswith('::ffff'):
                self.ip = self.ip.replace('::ffff:', '')

            if (self.ip == '127.0.0.1' or
                    self.ip.startswith('192.168.') or
                    self.ip.startswith('10.')):
                city_name = 'Local'
                country_name = 'Local'
                asn_name = 'Local'
            else:
                countries = list(db.execute(
                    country.select().where(
                        country.c.ipr.op('>>=')(visit['ip']))))

                if len(countries) > 0:
                    country_name = countries[0].country_name
                    country_code = countries[0].country_code
                    cities = list(db.execute(
                        city.select().where(
                            city.c.ipr.op('>>=')(visit['ip']))))
                    if len(cities) > 0:
                        city_name = cities[0].city
                        lat = cities[0].latitude
                        lng = cities[0].longitude
                asns = list(db.execute(
                    asn.select().where(
                        asn.c.ipr.op('>>=')(visit['ip']))))
                if len(asns) > 0:
                    asn_name = asns[0].asn

            visit['country'] = country_name
            visit['country_code'] = country_code
            visit['city'] = city_name
            visit['lat'] = lat
            visit['lng'] = lng
            visit['asn'] = asn_name
            visit = Visit(**visit)
            db.add(visit)

        self.log.info('%r inserted' % self)

        return visit, kind == 'o'
