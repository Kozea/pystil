#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2011 by Florian Mounier, Kozea
# This file is part of pystil, licensed under a 3-clause BSD license.

from flask import render_template, request, redirect, url_for
from uuid import uuid4


def register_admin_routes(app, route):
    """Defines admin routes"""
    from pystil.db import Visit, Keys
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

    @route('/keys/<int:id>/rm', methods=("POST",))
    def rm_key(id):
        """Remove a key"""
        key = Keys.all.filter(c.id == id).one(None).execute()
        if key:
            key.delete()
        return redirect(url_for('keys'))
