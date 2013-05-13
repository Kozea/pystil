# -*- coding: utf-8 -*-
# Copyright (C) 2011-2013 by Florian Mounier, Kozea
# This file is part of pystil, licensed under a 3-clause BSD license.

from pystil.db import Visit, count
from pystil.tracking import Tracking
from pystil.aggregates import get_attribute_and_count
from pystil.context import Hdr, url
from tornado.web import asynchronous
from sqlalchemy import desc
import os
import uuid


@url(r'/')
class Index(Hdr):
    def get(self):
        self.render('index.html')


@url(r'/pystil.js')
class PystilJs(Hdr):
    def get(self):
        self.set_header("Content-Type", 'application/javascript')
        js = os.path.join(
            self.application.settings['static_path'],
            'js', 'tracker.js')
        base_url = '%s://%s/' % (self.request.protocol, self.request.host)
        with open(js) as js_file:
            self.write(js_file.read() % (base_url, str(uuid.uuid4())))


@url(r'/pystil-(\d+).gif')
class Tracker(Hdr):

    @asynchronous
    def get(self, stamp):
        self.set_header("Content-Type", 'image/gif')
        gif_fn = os.path.join(
            self.application.settings['static_path'], 'pystil.gif')

        with open(gif_fn, 'rb') as gif_file:
            self.write(gif_file.read())
        self.finish()
        Tracking(
            self.db,
            self.request.arguments,
            self.request.headers['User-Agent'],
            self.request.remote_ip)


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
        self.render('sites.html', sites=sites, all_=all_)


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
        self.render('sites_table.html', sites=sites)


@url(r'/site/([^/]+)')
class Site(Hdr):
    def get(self, site):
        """Stats per site or all if site = all"""
        self.render('site.html', site=site)
