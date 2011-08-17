#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2011 by Florian Mounier, Kozea
# This file is part of pystil, licensed under a 3-clause BSD license.

from flask import render_template, Response, abort
from multicorn.requests import CONTEXT as c
import csstyle


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
        return render_template('site.jinja2', site=site or '*')

    @route("/css.css")
    def css():
        """Render the css with some url_for in it"""
        text = render_template('css/css.jinja2')
        for browser in csstyle.BROWSERS:
            browser_parser = getattr(csstyle, browser)
            text += '\n\n/* CSS for %s */\n\n' % browser
            parser = csstyle.Parser(text=render_template('css/css.jinja2'))
            text += repr(browser_parser.transform(parser, keep_existant=False))
        return Response(text, mimetype='text/css')

    @route("/<site>/graphs.js")
    def graphs(site):
        """Render the graph js with some url_for in it"""
        return Response(render_template('js/graphs.js', site=site),
                        mimetype='text/javascript')
