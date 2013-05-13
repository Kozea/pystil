# -*- coding: utf-8 -*-
# Copyright (C) 2011-2013 by Florian Mounier, Kozea
# This file is part of pystil, licensed under a 3-clause BSD license.

from datetime import date, timedelta
from pystil.utils import on, between, parse_referrer
from pystil.context import Hdr, url
from pystil.db import Visit, count, distinct
from pystil.i18n import labelize, titlize
from pystil.aggregates import get_attribute_and_count
from sqlalchemy import desc
import pygal
from pygal.style import Style
from pygal.util import cut


PystilStyle = Style(
    background='transparent',
    plot_background='rgba(255, 255, 255, .2)',
    foreground='#73716a',
    foreground_dark='#73716a',
    foreground_light='#be3e3a',
    opacity='.4',
    opacity_hover='.6',
    transition='500ms',
    colors=(
        "#ca4869",
        "#a54ca1",
        "#504ca5",
        "#4a80ad",
        "#49b4b0",
        "#4ca55d",
        "#a6af44",
        "#eac516",
        "#ea9316",
        "#bb6120",
        "#951313"
    ))


class Chart(object):
    def __init__(self, db, site, criteria, from_date, to_date):
        self.db = db
        self.site = site
        self.criteria = criteria
        self.from_date = from_date
        self.to_date = to_date
        self.table = Visit.__table__
        self.criterion = None
        self.chart = None
        self.count_col = None

    def get_chart(self):
        return self.type(
            interpolate='cubic',
            fill=True,
            truncate_legend=200,
            style=PystilStyle,
            width=1000,
            height=400,
            legend_at_bottom=self.type != Pie)

    def get_restrict(self):
        if self.criterion is not None:
            return self.criterion != None
        return True

    def filter(self, query):
        return (query
                .filter(on(self.site, self.table))
                .filter(between(self.from_date, self.to_date, self.table))
                .filter(self.get_restrict()))

    def get_query(self):
        self.table, self.criterion, self.count_col = get_attribute_and_count(
            self.criteria)
        return (
            self.filter(self.db.query(
                self.criterion.label("key"), self.count_col.label("count")))
            .group_by(self.criterion))

    def render(self):
        self.chart = self.get_chart()
        self.populate()
        self.chart.title = titlize(self.criteria, 'us')
        return self.chart.render()


class Line(Chart):
    type = pygal.Line

    def populate(self):
        all = (self.filter(self.db
               .query(Visit.day, count(1), count(distinct(Visit.uuid))))
               .group_by(Visit.day)
               .order_by(Visit.day)
               .all())

        self.chart.x_labels = list(map(
            lambda x: x.strftime('%Y-%m-%d'), cut(all, 0)))
        self.chart.add(labelize('all', 'us'), cut(all, 1))
        self.chart.add(labelize('unique', 'us'), cut(all, 2))

        new = (
            self.db
            .query(count(distinct(Visit.uuid)))
            .filter(Visit.last_visit == None)
            .group_by(Visit.day)
            .order_by(Visit.day)
            .all())
        self.chart.add(labelize('new', 'us'), cut(new, 0))
        self.chart.x_label_rotation = 45


class Bar(Chart):
    type = pygal.Bar

    def populate(self):
        all = self.get_query().order_by(self.criterion).all()
        self.chart.x_labels = list(map(str, cut(all, 0)))
        self.chart.add(labelize(self.criteria, 'us'),
                       list(map(float, cut(all, 1))))


class Pie(Chart):
    type = pygal.Pie

    def get_restrict(self):
        # Multi criteria restrict
        if self.criteria == 'browser_name_version':
            return (
                (self.table.c.browser_name != None) &
                (self.table.c.browser_version != None))
        return super(Pie, self).get_restrict()

    def populate(self):
        results = (self.get_query()
                   .order_by(desc(self.count_col))
                   .limit(10)
                   .all())
        visits = [{
            'label': (
                parse_referrer(visit.key, host_only=True, second_pass=True)
                if self.criteria == 'pretty_referrer' else visit.key),
            'data': visit.count
        } for visit in results]
        all_visits = (self.filter(self.db
                      .query(self.count_col.label("all")))
                      .first()).all or 0
        other = all_visits - sum(visit['data'] for visit in visits)
        if other:
            visits = visits + [{'label': 'Other', 'data': other}]

        for visit in visits:
            self.chart.add(str(visit['label']), float(visit['data']))


@url(r'/load/data/([^/]+)/([^/]+)/([^/]+).svg')
class LoadData(Hdr):
    def get(self, site, type_, criteria):
        self.set_header("Content-Type", "image/svg+xml")
        chart = getattr(pygal, type_)(
            fill=True,
            style=PystilStyle,
            width=1000,
            height=400)
        chart.no_data_text = 'Loading'
        chart.title = titlize(criteria, 'us')
        self.write(chart.render())


@url(r'/data/([^/]+)/([^/]+)/([^/]+).svg')
class Data(Hdr):
    def get(self, site, type_, criteria):
        self.set_header("Content-Type", "image/svg+xml")
        from_date = date.today() - timedelta(days=31)
        to_date = date.today()
        chart = globals()[type_](self.db, site, criteria, from_date, to_date)
        self.write(chart.render())
