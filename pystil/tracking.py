# -*- coding: utf-8 -*-
# Copyright (C) 2011-2013 by Florian Mounier, Kozea
# This file is part of pystil, licensed under a 3-clause BSD license.

from pystil.utils import (
    try_decode, parse_ua, parse_referrer, parse_domain)
from pystil.db import Visit, country, city, asn, VisitIdSeq
from datetime import datetime, timedelta
from sqlalchemy import desc, select


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
        self.log.debug('Processing message %r' % self)
        visits = Visit.__table__
        if len(self.qs_args) == 0:
            raise ValueError('No params in request. Must be a bot.')

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
        if kind == 'e':
            raise RuntimeError('Problem in tracker: "%s"' % get('r'))
        uuid = get('_')
        if '; ' in uuid:
            uuid = uuid.split('; ')[0]
        platform, browser, version = parse_ua(self.ua)
        if kind == 'c':
            try:
                id = db.execute(
                    select([visits.c.id])
                    .where(visits.c.uuid == uuid)
                    .order_by(desc(visits.c.date))
                ).fetchone()['id']
            except:
                self.log.warn('Could not find uuid %s' % uuid, exc_info=True)
            else:
                db.execute(
                    visits
                    .update()
                    .where(visits.c.id == id)
                    .values(time=timedelta(seconds=int(get('t', 0)) / 1000)))
                self.log.debug('%r inserted' % self)
            return uuid, False

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
                     'query': get('q'),
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
            elif self.ip != 'unknown':
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
            domain_parts = visit['host'].split('.')
            if len(domain_parts) > 2:
                visit['subdomain'] = '.'.join(domain_parts[:-2])
            else:
                visit['subdomain'] = None
            visit['domain'] = '.'.join(domain_parts[-2:])
            visit['day'] = visit['date'].date()
            visit['hour'] = visit['date'].hour
            browser_minor_version = ''
            if (
                    visit['browser_name'] not in ('opera', 'safari', 'chrome') and
                    len(visit['browser_version'].split('.')) > 1):
                browser_minor_version = '.%s' % visit['browser_version'].split('.')[1]

            visit['browser_name_version'] = '%s %s%s' % (visit['browser_name'],
                                                         visit['browser_version'].split('.')[0],
                                                         browser_minor_version)
            visit['id'] = db.execute(select([VisitIdSeq.next_value()])).scalar()
            db.execute(visits.insert().returning(visits.c.id), **visit)
            self.log.debug('%r inserted' % self)
            return visit, True

        raise NotImplementedError('Unknown kind %s' % kind)
