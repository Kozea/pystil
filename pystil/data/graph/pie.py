#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2011 by Florian Mounier, Kozea
# This file is part of pystil, licensed under a 3-clause BSD license.

"""Treat pie data"""


from multicorn.requests import CONTEXT as c
from pystil.data.utils import (top, transform_for_pie, base_request,
                               cut_browser_version, parse_referrer)


def process_data(site, graph, criteria, from_date, to_date, step, stamp):
    rq = base_request(site, from_date, to_date)
    if criteria == 'browser_version':
        visits = (rq
                  .filter((c.browser_name != None) &
                          (c.browser_version != None))
                  .map({'label': c.browser_name + ' ' + c.browser_version,
                        'data': 1})
                  .execute())
        version_visits = {}
        for visit in visits:
            data = visit['data']
            label = cut_browser_version(visit['label'])
            if label in version_visits:
                version_visits[label] += data
            else:
                version_visits[label] = data
        visits = [
            {'label': key, 'data': value}
            for key, value in top(version_visits)]
        return {'list': visits}

    rq = (rq.filter(getattr(c, criteria) != None)
              .groupby(getattr(c, criteria), count=c.len())
              .sort(-c.count))

    if criteria == 'referrer':
        results = {}
        for referrer in rq.execute():
            host = parse_referrer(referrer['key'], host_only=True)
            results[host] = results.get(host, 0) + referrer['count']
        results = [{'label': key,
                    'data': value} for key, value in top(results)]
        return {'list': results}
    return transform_for_pie(rq[:10].execute(), site)
