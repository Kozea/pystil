from pystil.data.utils import (
    try_decode, parse_ua, parse_referrer, parse_domain)
from pystil.db import Visit
from threading import Thread
from datetime import datetime, timedelta
from sqlalchemy import desc


class Tracking(Thread):
    def __init__(self, db, qs_args, ua, ip, *args, **kwargs):
        super(Tracking, self).__init__(*args, **kwargs)
        self.db = db
        self.qs_args = qs_args
        self.ua = ua
        self.stamp = datetime.utcnow()
        self.ip = ip
        self.start()

    def run(self):
        self.db()

        def get(key, default=None, from_encoding=None):
            value = self.qs_args.get(key, [default])[0]
            if value and value == b'undefined':
                value = None
            if value:
                if from_encoding:
                    value = value.decode(from_encoding)
                else:
                    value = try_decode(value)
            return value

        kind = get('d')
        uuid = get('_')
        platform, browser, version = parse_ua(self.ua)

        if kind == 'o':
            last_visit = get('l')
            if last_visit and 'undefined' not in last_visit:
                last_visit = datetime.fromtimestamp(int(last_visit) / 1000)
            else:
                last_visit = None
            visit = {'uuid': uuid,
                     'host': get('k'),
                     'site': get('u'),
                     'client_tz_offset': get('z', 0),
                     'date': self.stamp,
                     'last_visit': last_visit,
                     'ip': self.ip,
                     'referrer': get('r'),
                     'pretty_referrer': parse_referrer(
                         get('r', from_encoding='latin-1')),
                     'referrer_domain': parse_domain(
                         get('r', from_encoding='latin-1')),
                     'size': get('s'),
                     'page': get('p', from_encoding='latin-1'),
                     'hash': get('h', from_encoding='latin-1'),
                     'query_string': get('q'),
                     'language': get('i'),
                     'browser_name': browser,
                     'browser_version': version,
                     'platform': platform}
            # self.add_geolocalization(visit)
            self.db.add(Visit(**visit))
            self.db.commit()
            return visit
        if kind == 'c':
            visit = (self.db
                     .query(Visit)
                     .filter(Visit.uuid == uuid)
                     .order_by(desc(Visit.date))
                     .first())
            if visit:
                visit.time = timedelta(seconds=int(get('t', 0)) / 1000)
                self.db.commit()
