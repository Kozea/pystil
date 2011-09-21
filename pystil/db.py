#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2011 by Florian Mounier, Kozea
# This file is part of pystil, licensed under a 3-clause BSD license.
from flaskext.sqlalchemy import SQLAlchemy
from sqlalchemy import func, desc
from sqlalchemy.orm import column_property
from sqlalchemy.sql.expression import case

db = SQLAlchemy()
count = func.count
distinct = func.distinct
date_part = func.date_part
date_trunc = func.date_trunc
split_part = func.split_part
strpos = func.strpos
substr = func.substr
length = func.length
array_agg = func.array_agg


def string():
    return db.Column(db.String)


def integer(pkey=False):
    return db.Column(db.Integer, primary_key=pkey)


def decimal():
    return db.Column(db.Numeric)


def datetime():
    return db.Column(db.DateTime)


def fields(clazz):
    return [field
            for field in clazz.__dict__
            if not field.startswith("_")]


class Visit(db.Model):
    """This mapped class contains the visits"""

    id = integer(pkey=True)
    uuid = string()
    browser_name = string()
    hash = string()
    host = string()
    browser_version = string()
    client_tz_offset = integer()
    date = datetime()
    last_visit = datetime()
    ip = string()
    language = string()
    page = string()
    platform = string()
    query_string = db.Column('query', db.String)
    referrer = string()
    pretty_referrer = string()
    site = string()
    size = string()
    time = integer()
    country = string()
    country_code = string()
    city = string()
    lat = decimal()
    lng = decimal()

    browser_name_version = column_property(
        browser_name + ' ' + split_part(browser_version, '.', 1) +
        case([
            (browser_name.in_(['opera', 'safari', 'chrome']), '')],
            else_='.' + split_part(browser_version, '.', 2)
            ))

    day = column_property(
        date_trunc('day', date))

    hour = column_property(
        date_part('hour', date))

    spent_time = column_property(
        case([
            (time == None, None),
            (time < 1000, 0),
            (time < 2000, 1),
            (time < 5000, 2),
            (time < 10000, 3),
            (time < 20000, 4),
            (time < 30000, 5),
            (time < 60000, 6),
            (time < 120000, 7),
            (time < 300000, 8),
            (time < 600000, 9)
        ], else_=10))

    subdomain = column_property(
        case([
            (split_part(host, '.', 3) != '', split_part(host, '.', 1))
        ], else_=None))

    domain = column_property(
        case([
            (split_part(host, '.', 3) == '', host),
        ], else_=substr(host,
                        strpos(host, '.') + 1,
                        length(host) - strpos(host, '.') + 1)))


class Keys(db.Model):
    """This mapped lass contains the auth keys"""

    id = integer(pkey=True)
    key = string()
    host = string()
