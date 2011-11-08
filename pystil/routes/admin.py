#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2011 by Florian Mounier, Kozea
# This file is part of pystil, licensed under a 3-clause BSD license.

from flask import render_template, request, redirect, url_for
from uuid import uuid4
from sqlalchemy import func
from pystil.db import db, distinct, Visit, Keys


def register_admin_routes(app, route):
    """Defines admin routes"""
    log = app.logger

    @route('/keys')
    def keys():
        """List the auth keys"""
        keys = Keys.query.order_by(Keys.host, Keys.key).all()
        hosts = (db.session
                 .query(distinct(Visit.host).label('host'))
                 .all())
        return render_template('keys.jinja2', keys=keys, hosts=hosts)

    @route('/keys/add', methods=("POST",))
    def add_key():
        """Add a key"""
        uuid = uuid4()
        key = Keys(host=request.values['host'], key=str(uuid))
        db.session.add(key)
        db.session.commit()
        return redirect(url_for('keys'))

    @route('/keys/<int:id>/rm', methods=("POST",))
    def rm_key(id):
        """Remove a key"""
        key = Keys.query.get(id)
        if key:
            db.session.delete(key)
            db.session.commit()
        return redirect(url_for('keys'))
