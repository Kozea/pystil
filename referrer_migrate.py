#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2011 by Florian Mounier, Kozea
# This file is part of pystil, licensed under a 3-clause BSD license.
from pystil import config
from pystil.data.utils import parse_referrer
from sqlalchemy.ext.sqlsoup import SqlSoup

config.freeze()

db = SqlSoup(config.CONFIG["DB_URL"])
Visit = db.visit
for i in xrange(0, Visit.filter(Visit.referrer != None).count(), 20):
    print "from %d to %d" % (i, i + 20)
    for visit in Visit.filter(Visit.referrer != None)[i:i + 20]:
        visit.pretty_referrer = parse_referrer(visit.referrer)
    db.commit()
