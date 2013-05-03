#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2011 by Florian Mounier, Kozea
# This file is part of pystil, licensed under a 3-clause BSD license.

from pystil.db import Visit, count
from pystil.aggregates import get_attribute_and_count
from pystil.context import Hdr, url
from sqlalchemy import desc


@url(r'/')
class Index(Hdr):
    def get(self):
        all_ = self.db.query(count(1)).select_from(Visit).scalar()
        self.render('index.jinja2', all_=all_)


@url(r'/sites')
class Sites(Hdr):
    def get(self):
        """List of sites"""
        table, attr, countcol = get_attribute_and_count('domain')
        sites = (
            self.db
            .query(attr, countcol.label('count'))
            .group_by(attr)
            .order_by(desc(countcol)))[:20]
        all_ = self.db.query(countcol).scalar()
        self.render('sites.jinja2', sites=sites, all_=all_)


@url(r'/sites/([^/])')
class SitesQuery(Hdr):
    def get(self, query):
        """Sites matching query"""
        sites = (
            self.db
            .query(Visit.host, count(1).label('count'))
            .filter(Visit.host.like('%%%s%%' % query))
            .group_by(Visit.host)
            .order_by(desc('count')))[:20]
        self.render('sites_table.jinja2', sites=sites)


@url(r'/site/([^/]+)')
class Site(Hdr):
    def get(self, site):
        """Stats per site or all if site = all"""
        self.render('site.jinja2', site=site)
