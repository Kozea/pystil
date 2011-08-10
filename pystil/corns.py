#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2011 by Florian Mounier, Kozea
# This file is part of pystil, licensed under a 3-clause BSD license.
from datetime import datetime
from multicorn import Multicorn
from multicorn.corns.alchemy import Alchemy
from multicorn.declarative import declare, Property

MC = Multicorn()


@MC.register
@declare(Alchemy, identity_properties=['uuid'], url='sqlite:///pystil.db')
class Visit(object):
    """This corn contains the visits"""
    uuid = Property()
    browser_name = Property()
    hash = Property()
    browser_version = Property()
    date = Property(type=datetime)
    ip = Property()
    language = Property()
    page = Property()
    platform = Property()
    query = Property()
    referrer = Property()
    site = Property()
    size = Property()
    time = Property(type=int)
