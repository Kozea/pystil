#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2011 by Florian Mounier, Kozea
# This file is part of pystil, licensed under a 3-clause BSD license.
from flaskext.sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def string():
    return db.Column(db.String)


def integer(pkey=False):
    return db.Column(db.Integer, primary_key=pkey)


def decimal():
    return db.Column(db.Numeric)


def datetime():
    return db.Column(db.DateTime)


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
    site = string()
    size = string()
    time = integer()
    country = string()
    country_code = string()
    city = string()
    lat = decimal()
    lng = decimal()


class Keys(db.Model):
    """This corn contains the auth keys"""

    id = integer(pkey=True)
    key = string()
    host = string()
