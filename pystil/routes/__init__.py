#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2011 by Florian Mounier, Kozea
# This file is part of pystil, licensed under a 3-clause BSD license.

from flask import render_template, Response, abort
import csstyle
import os
import pystil
from pystil.db import db, Visit
from sqlalchemy import func, desc


def register_common_routes(app, route):
    """Defines common routes"""
    log = app.logger

    @route('/')
    def index():
        """List of sites"""
        sites = (db.session
                 .query(func.count(Visit.host).label('count'),
                        Visit.host.label('host'))
                 .group_by(Visit.host).order_by(desc('count')).all())
        all_ = db.session.query(func.count('*')).select_from(Visit).scalar()

        return render_template('index.jinja2', sites=sites, all_=all_)

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
