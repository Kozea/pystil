# -*- coding: utf-8 -*-
# Copyright (C) 2011-2013 by Florian Mounier, Kozea
# This file is part of pystil, licensed under a 3-clause BSD license.

from datetime import date, timedelta
from pystil.utils import on, between
from pystil.context import Hdr, url
from pystil.aggregates import get_attribute_and_count
from pygal.util import cut
from lxml import etree
import os


with open(os.path.join(os.path.dirname(__file__), 'map.svg')) as map_file:
    MAP = map_file.read()


@url(r'/data/([^/]+)/map.svg')
class Map(Hdr):
    def get(self, site):
        self.set_header("Content-Type", "image/svg+xml")
        from_date = date.today() - timedelta(days=31)
        to_date = date.today()
        table, criteria, count_col = get_attribute_and_count('country_code')
        all = (
            self.db
            .query(
                table.c.country,
                table.c.country_code,
                count_col.label("count"))
            .filter(on(site, table))
            .filter(between(from_date, to_date, table))
            .group_by(table.c.country_code, table.c.country)
            .all())
        visit_max = float(max(cut(all, 2) or [1]))
        map = etree.fromstring(MAP)
        for visit in all:
            country = map.find('.//*[@id="%s"]' % visit.country_code.lower())
            if country is not None:
                country.set('style', 'fill: rgba(0, 0, 255, %f)' % (
                    (float(visit.count) / visit_max) * .7 + .2))
                title = etree.Element('title')
                title.text = '%s: %d' % (visit.country.lower(), visit.count)
                country.insert(0, title)
        self.write(etree.tostring(map))
