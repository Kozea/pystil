#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2011 by Florian Mounier, Kozea
# This file is part of pystil, licensed under a 3-clause BSD license.
from flaskext.sqlalchemy import SQLAlchemy
from datetime import timedelta
from sqlalchemy import func, desc
from sqlalchemy.orm import column_property
from sqlalchemy.sql.expression import case
from . import patchpsycopg

db = SQLAlchemy()
count = func.count
sum_ = func.sum
distinct = func.distinct
date_part = func.date_part
date_trunc = func.date_trunc
split_part = func.split_part
strpos = func.strpos
substr = func.substr
length = func.length
array_agg = func.array_agg


def string(pkey=False):
    return db.Column(db.String, primary_key=pkey)


def integer(pkey=False):
    return db.Column(db.Integer, primary_key=pkey)


def decimal():
    return db.Column(db.Numeric)


def datetime():
    return db.Column(db.DateTime)


def date(pkey=False):
    return db.Column(db.Date, primary_key=pkey)


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
    referrer_domain = string()
    site = string()
    size = string()
    time = db.Column(db.Interval)
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
            (time < timedelta(seconds=1), 0),
            (time < timedelta(seconds=2), 1),
            (time < timedelta(seconds=5), 2),
            (time < timedelta(seconds=10), 3),
            (time < timedelta(seconds=20), 4),
            (time < timedelta(seconds=30), 5),
            (time < timedelta(seconds=60), 6),
            (time < timedelta(seconds=120), 7),
            (time < timedelta(seconds=300), 8),
            (time < timedelta(seconds=600), 9)
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
