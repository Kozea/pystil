from functools import reduce
from pystil.db import Visit, count, sum_
from pystil.context import pystil

db = pystil.db
metadata = pystil.db_metadata
engine = pystil.db_engine


class memoized(object):

    def __init__(self, func):
        self.func = func
        self.cache = {}

    def __call__(self, *args):
        value = self.cache.get(args, None)
        if value is None:
            value = self.cache[args] = self.func(*args)
        return value


@memoized
def init_if_needed():
    metadata.reflect(bind=engine, schema='agg')


def key_with_min_value(item1, item2):
    key1, value1 = item1
    key2, value2 = item2
    if value1 > value2:
        return item2
    else:
        return item1


@memoized
def get_aggregate_table(attr_name):
    """Return the best aggregate table for the given attribute"""
    init_if_needed()
    scores = {}
    for tablename, table in metadata.tables.items():
        if table.schema == 'agg' and hasattr(table.c, attr_name):
            scores[table] = len(table.c)
    # Magic number 9999: if the table has more than 50 columns, it is probably
    # a really bad aggregate
    table, score = reduce(key_with_min_value, scores.items(), (None, 50))
    return table


@memoized
def get_attribute_and_count(attr_name):
    """Return a tuple of (table, attr_col, count_column) according to the best
    aggregate table
    """
    if attr_name == 'day':
        # all tables work on the day column
        attr_name = 'date'
    table = get_aggregate_table(attr_name)
    if table is None:
        table = Visit.__table__
        pystil.log.warn('No aggregate table found for %s' % attr_name)
        countcol = count(1)
        attr = getattr(Visit, attr_name)
    else:
        countcol = sum_(table.c.fact_count)
        attr = getattr(table.c, attr_name)
    return table, attr, countcol
