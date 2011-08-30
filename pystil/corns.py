#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2011 by Florian Mounier, Kozea
# This file is part of pystil, licensed under a 3-clause BSD license.
from datetime import datetime
from decimal import Decimal

from pystil import config
from multicorn import Multicorn
from multicorn.requests import CONTEXT as c, case, when
from multicorn.corns.alchemy import Alchemy
from multicorn.declarative import declare, Property, computed

MC = Multicorn()


@MC.register
@declare(Alchemy, identity_properties=['id'], url=config.CONFIG["DB_URL"])
class Visit(object):
    """This corn contains the visits"""
    id = Property(type=int)
    uuid = Property()
    browser_name = Property()
    hash = Property()
    host = Property()
    browser_version = Property()
    client_tz_offset = Property(type=int)
    date = Property(type=datetime)
    last_visit = Property(type=datetime)
    ip = Property()
    language = Property()
    page = Property()
    platform = Property()
    query = Property()
    referrer = Property(type=str)
    site = Property()
    size = Property()
    time = Property(type=int)
    country = Property()
    country_code = Property()
    city = Property()
    lat = Property(type=Decimal)
    lng = Property(type=Decimal)

    @computed()
    def day(self):
        return c.date.str()[:10]

    @computed()
    def hour(self):
        return c.date.str()[11:13]

    @computed()
    def spent_time(self):
        return case(
            when(c.time == None, None),
            when(c.time < 1000, 0),
            when(c.time < 2000, 1),
            when(c.time < 5000, 2),
            when(c.time < 10000, 3),
            when(c.time < 20000, 4),
            when(c.time < 30000, 5),
            when(c.time < 60000, 6),
            when(c.time < 120000, 7),
            when(c.time < 300000, 8),
            when(c.time < 600000, 9),
            10)


@MC.register
@declare(Alchemy, identity_properties=['id'], url=config.CONFIG["DB_URL"])
class Keys(object):
    """This corn contains the auth keys"""
    id = Property(type=int)
    key = Property()
    host = Property()
