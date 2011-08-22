#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2011 by Florian Mounier, Kozea
# This file is part of pystil, licensed under a 3-clause BSD license.

from flask import render_template, Response, abort
from multicorn.requests import CONTEXT as c
import csstyle
import os
import pystil


def register_common_routes(app, route):
    """Defines common routes"""
    from pystil.corns import Visit
    log = app.logger

    @route('/')
    def index():
        """List of sites"""
        sites = list(
            Visit.all
            .map(c.host)
            .groupby(c, count=c.len())
            .sort(-c.count)
            .execute())
        all_ = Visit.all.len().execute()
        return render_template('index.jinja2', sites=sites, all_=all_)

    @route('/favicon.ico')
    def favicon():
        abort(404)

    @route('/<site>')
    def site(site):
        """Stats per site or all if site = *"""
        return render_template('site.jinja2', site=site)

    @route('/<site>/map')
    def map(site):
        """Stats per site or all if site = *"""
        return render_template('map.jinja2', site=site)

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
