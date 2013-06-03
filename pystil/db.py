# -*- coding: utf-8 -*-
# Copyright (C) 2011-2013 by Florian Mounier, Kozea
# This file is part of pystil, licensed under a 3-clause BSD license.

from datetime import timedelta
from sqlalchemy import func
from sqlalchemy.orm import column_property
from sqlalchemy.sql.expression import case
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (
    Column, Integer, String, Numeric, DateTime, Date, Interval, Table,
    Sequence)

Base = declarative_base()
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
    return Column(String, primary_key=pkey)


def integer(pkey=False):
    return Column(Integer, primary_key=pkey)


def decimal():
    return Column(Numeric)


def datetime():
    return Column(DateTime)


def date_column(pkey=False):
    return Column(Date, primary_key=pkey)


class Visit(Base):
    """This mapped class contains the visits"""
    __tablename__ = 'visit'

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
    query = string()
    referrer = string()
    pretty_referrer = string()
    referrer_domain = string()
    site = string()
    size = string()
    time = Column(Interval)
    country = string()
    country_code = string()
    city = string()
    lat = decimal()
    lng = decimal()
    asn = string()

    browser_name_version = string()
    day = date_column()
    hour = integer()
    subdomain = string()
    domain = string()

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


class CriterionView(Base):
    __tablename__ = 'criterion_view'

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
    query = string()
    referrer = string()
    pretty_referrer = string()
    referrer_domain = string()
    site = string()
    size = string()
    time = Column(Interval)
    country = string()
    country_code = string()
    city = string()
    lat = decimal()
    lng = decimal()
    asn = string()

    browser_name_version = string()
    day = date_column()
    hour = integer()
    subdomain = string()
    domain = string()


VisitIdSeq = Sequence('visit_id_seq')

metadata = Base.metadata


# Geoip database
country = Table(
    'country', metadata,
    Column('ipr', String),
    Column('country_code', String),
    Column('country_name', String),
    schema='geoip'
)

city = Table(
    'city', metadata,
    Column('ipr', String),
    Column('country_code', String),
    Column('region', String),
    Column('city', String),
    Column('postal_code', String),
    Column('latitude', Numeric),
    Column('longitude', Numeric),
    Column('metro_code', Integer),
    Column('area_code', Integer),
    schema='geoip'
)

asn = Table(
    'asn', metadata,
    Column('ipr', String),
    Column('asn', String),
    schema='geoip'
)
