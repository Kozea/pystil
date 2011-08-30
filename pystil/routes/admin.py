#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2011 by Florian Mounier, Kozea
# This file is part of pystil, licensed under a 3-clause BSD license.

from flask import render_template, request, redirect, url_for
from multicorn.requests import CONTEXT as c
from uuid import uuid4


def register_admin_routes(app, route):
    """Defines admin routes"""
    from pystil.corns import Visit, Keys
    log = app.logger

    @route('/keys')
    def keys():
        """List the auth keys"""
        keys = Keys.all.sort(c.host, c.key).execute()
        hosts = Visit.all.map(c.host).distinct().sort().execute()
        return render_template('keys.jinja2', keys=keys, hosts=hosts)

    @route('/keys/add', methods=("POST",))
    def add_key():
        """Add a key"""
        uuid = uuid4()
        Keys.create({'host': request.values['host'], 'key': str(uuid)}).save()
        return redirect(url_for('keys'))
