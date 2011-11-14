#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2011 by Florian Mounier, Kozea
# This file is part of pystil, licensed under a 3-clause BSD license.

from flask import render_template, Response
import csstyle
import os
import pystil
from pystil.db import db, Visit, count, desc
from pystil.aggregates import get_attribute_and_count


def register_common_routes(app, route):
    """Defines common routes"""
    log = app.logger

    @route('/')
    def index():
        all_ = db.session.query(count(1)).select_from(Visit).scalar()
        return render_template('index.jinja2', all_=all_)

    @route('/sites')
    def sites():
        """List of sites"""
        table, attr, countcol = get_attribute_and_count('domain')
        sites = (
            db.session
            .query(attr, countcol.label('count'))
            .group_by(table)
            .order_by(countcol))[:20]
        all_ = db.session.query(countcol).scalar()
        return render_template('sites.jinja2', sites=sites, all_=all_)

    @route('/sites/<query>')
    def sites_query(query):
        """Sites matching query"""
        sites = (
            db.session
            .query(Visit.host, count(1).label('count'))
            .filter(Visit.host.like('%%%s%%' % query))
            .group_by(Visit.host)
            .order_by(desc('count')))[:20]
        return render_template('sites_table.jinja2', sites=sites)

    @route('/<site>')
    def site(site):
        """Stats per site or all if site = all"""
        return render_template('site.jinja2', site=site)

    @route("/css.css")
    def css():
        """Render the css with CSStyle"""
        style = os.path.join(
            os.path.dirname(os.path.abspath(pystil.__file__)),
            'static', 'css.css')
        with open(style) as style:
            text = style.read()

        for browser in csstyle.BROWSERS:
            browser_parser = getattr(csstyle, browser)
            text += '\n\n/* CSS for %s */\n\n' % browser
            parser = csstyle.Parser(text=text)
            text += repr(browser_parser.transform(parser, keep_existant=False))
        return Response(text, mimetype='text/css')
