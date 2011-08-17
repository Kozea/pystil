#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2011 by Florian Mounier, Kozea
# This file is part of pystil, licensed under a 3-clause BSD license.
from pystil import config
config.freeze()

from pystil.corns import Visit
from pygeoip import GeoIP, MMAP_CACHE
import re


gip = GeoIP(config.CONFIG['IP_DB'], MMAP_CACHE)
IPV4RE = re.compile(r"(\d{1,3}(\.|$)){4}")


for visit in Visit.all.execute():
    lat = None
    lng = None
    ip = visit['ip']
    ip = ip.replace('::ffff:', '')
    if IPV4RE.match(ip):
        if (ip == '127.0.0.1'
            or ip.startswith('192.168.')
            or ip.startswith('10.')):
            city = 'Local'
            country = 'Local'
        else:
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
    visit.save()
    print city, " done"
