#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2011 by Florian Mounier, Kozea
# This file is part of pystil, licensed under a 3-clause BSD license.


from datetime import datetime, date, timedelta
from functools import wraps
from pystil.data.utils import PystilEncoder, on, between, parse_referrer
from pystil.context import Hdr, url
from pystil.db import Visit, fields, count, distinct
from pystil.data import process_data
from pystil.data.utils import date_to_time, labelize, titlize
from pystil.aggregates import get_attribute_and_count
from sqlalchemy import desc
import pygal
from pygal.style import Style
from pygal.util import cut

import json

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

        from_date = date_to_time(date.today() - timedelta(days=31))
        to_date = date_to_time(date.today())

        if type_ == 'Line':
            all = (
                self.db
                .query(Visit.day, count(1), count(distinct(Visit.uuid)))
                .filter(on(site))
                .filter(between(
                    date_to_time(date.today() - timedelta(days=31)),
                    date_to_time(date.today())))
                .group_by(Visit.day)
                .order_by(Visit.day)
                .all())
            chart.x_labels = list(map(
                lambda x: x.strftime('%Y-%m-%d'), cut(all, 0)))
            chart.add(labelize('all', 'us'), cut(all, 1))
            chart.add(labelize('unique', 'us'), cut(all, 2))

            new = (
                self.db
                .query(count(1))
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


    def post(self):
        self.set_header("Content-Type", "application/json")
        today = date.today()
        month_start = today - timedelta(days=31)
        site = self.get_argument('site')
        graph = self.get_argument('graph')
        criteria = self.get_argument('criteria')
        lang = self.get_argument('lang')
        step = self.get_argument('step', 'day')
        stamp = self.get_argument('stamp', None)
        from_date = int(self.get_argument(
            'from', date_to_time(month_start)))
        to_date = int(self.get_argument('to', date_to_time(today)))
        self.write(json.dumps(
            process_data(
                site, graph, criteria, from_date, to_date, step, stamp, lang),
            cls=PystilEncoder))


# def jsonp(f):
#     """Wraps JSONified output for JSONP"""

#     """Require user authorization"""
#     @wraps(f)
#     def decorated_function(*args, **kwargs):
#         callback = request.args.get('callback', False)
#         if callback:
#             content = str(callback) + '(' + f(*args, **kwargs) + ')'
#             return current_app.response_class(
#                 content, mimetype='application/javascript')
#         else:
#             return f(*args, **kwargs)
#     return decorated_function


# def register_data_routes(app, route):
#     """Defines data routes"""

#     url_base = '/<string:site>/<any%r:graph>_by_<any%r:criteria>_in_<lang>' % (
#         ('pie', 'bar', 'line', 'table', 'map', 'last', 'top'),
#         tuple(fields(Visit)) + (
#             'all', 'unique', 'new'))
#     url_with_at = '%s_at_<int:stamp>' % url_base
#     url_with_from = '%s_from_<int:from_date>' % url_base
#     url_with_to = '%s_to_<int:to_date>' % url_with_from
#     url_with_step = '%s_step_<any%r:step>' % (url_with_to, (
#         'hour', 'day', 'week', 'year'))

#     @route('%s.json' % url_base)
#     @route('%s.json' % url_with_at)
#     @route('%s.json' % url_with_from)
#     @route('%s.json' % url_with_to)
#     @route('%s.json' % url_with_step)
#     @jsonp
#     def data(site, graph, criteria, lang,
#              from_date=None, to_date=None, step='day', stamp=None):
#         today = date.today()
#         month_start = datetime(today.year, today.month, 1)
#         from_date = from_date or date_to_time(month_start)
#         to_date = to_date or date_to_time(today)
#         return json.dumps(process_data(
#             site, graph, criteria, from_date, to_date, step, stamp, lang),
#                        cls=PystilEncoder)
