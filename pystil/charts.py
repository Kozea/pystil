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
        chart = getattr(pygal, type_)(
            interpolate='cubic',
            fill=True,
            truncate_legend=200,
            style=PystilStyle,
            width=1000,
            height=400,
            legend_at_bottom=type_ != 'Pie')

        from_date = date.today() - timedelta(days=31)
        to_date = date.today()

        if type_ == 'Line':
            all = (
                self.db
                .query(Visit.day, count(1), count(distinct(Visit.uuid)))
                .filter(on(site))
                .filter(between(from_date, to_date))
                .group_by(Visit.day)
                .order_by(Visit.day)
                .all())
            chart.x_labels = list(map(
                lambda x: x.strftime('%Y-%m-%d'), cut(all, 0)))
            chart.add(labelize('all', 'us'), cut(all, 1))
            chart.add(labelize('unique', 'us'), cut(all, 2))

            new = (
                self.db
                .query(count(distinct(Visit.uuid)))
                .filter(on(site))
                .filter(between(from_date, to_date))
                .filter(Visit.last_visit == None)
                .group_by(Visit.day)
                .order_by(Visit.day)
                .all())
            chart.add(labelize('new', 'us'), cut(new, 0))
            chart.x_label_rotation = 45

        if type_ == 'Pie':
            table, criterion, count_col = get_attribute_and_count(criteria)
            restrict = (criterion != None)
            if criteria == 'browser_name_version':
                restrict = ((table.c.browser_name != None) &
                            (table.c.browser_version != None))
            rq = (self.db
                  .query(criterion.label("key"),
                         count_col.label("count"))
                  .filter(on(site, table))
                  .filter(between(from_date, to_date, table=table))
                  .filter(restrict)
                  .group_by(criterion)
                  .order_by(desc(count_col)))
            results = rq.limit(10).all()
            visits = [{'label': (
                parse_referrer(visit.key, host_only=True, second_pass=True)
                if criteria == 'pretty_referrer' else visit.key),
                       'data': visit.count}
                      for visit in results]
            all_visits = (self.db
                          .query(count_col.label("all"))
                          .filter(on(site, table))
                          .filter(between(from_date, to_date, table=table))
                          .filter(restrict)
                          .first()).all or 0
            other = all_visits - sum(visit['data'] for visit in visits)
            if other:
                visits = visits + [{'label': 'Other', 'data': other}]

            for visit in visits:
                chart.add(str(visit['label']), float(visit['data']))

        if type_ == 'Bar':
            table, criterion, count_col = get_attribute_and_count(criteria)
            all = (
                self.db
                .query(criterion.label("key"),
                       count_col.label("count"))
                .filter(on(site, table))
                .filter(between(from_date, to_date, table))
                .order_by(criterion)
                .group_by(criterion)
                .all())
            chart.x_labels = list(map(str, cut(all, 0)))
            chart.add(labelize(criteria, 'us'), list(map(float, cut(all, 1))))

        chart.title = titlize(criteria, 'us')
        self.write(chart.render())
