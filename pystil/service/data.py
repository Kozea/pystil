import urlparse
from datetime import datetime
from werkzeug.useragents import UserAgent
from multicorn.requests import CONTEXT as c
from pygeoip import GeoIP, MMAP_CACHE
import threading
import re
from flask import current_app
from .. import config

ipv4re = re.compile(r"(\d{1,3}(\.|$)){4}")

gip_tl = threading.local()


class Message(object):

    def __init__(self, query, user_agent, remote_addr):
        self.query = query
        self.stamp = datetime.now()
        self.user_agent = user_agent
        self.remote_addr = remote_addr

    @property
    def gip(self):
        if not hasattr(gip_tl, 'gip'):
            gip_tl.gip = GeoIP(config.CONFIG['IP_DB'], MMAP_CACHE)
        return gip_tl.gip

    def process(self):
        from pystil.corns import Visit

        def get(key, default=None):
            value = request_args.get(key, [default])[0]
            if value and 'undefined' in value:
                value = None
            return value

        request_args = urlparse.parse_qs(self.query)
        kind = get('d')
        uuid = get('_')
        user_agent = UserAgent(self.user_agent)
        if kind == 'o':
            last_visit = get('l')
            if last_visit and 'undefined' not in last_visit:
                last_visit = datetime.fromtimestamp(int(last_visit) / 1000)
            else:
                last_visit = None
            visit = {}
            visit['uuid'] = uuid
            visit['host'] = get('k')
            visit['site'] = get('u')
            visit['client_tz_offset'] = get('z', 0)
            visit['date'] = datetime.now()
            visit['last_visit'] = last_visit
            visit['ip'] = self.remote_addr
            visit['referrer'] = get('r')
            visit['size'] = get('s')
            visit['page'] = get('p')
            visit['hash'] = get('h')
            visit['query'] = get('q')
            visit['language'] = get('i')
            visit['browser_name'] = user_agent.browser
            visit['browser_version'] = user_agent.version
            visit['platform'] = user_agent.platform
            self.add_geolocalization(visit)
            current_app.logger.warn(visit)
            visit = Visit.create(visit)
            visit.save()
        elif kind == 'c':
            visit = next(
                Visit.all.filter(c.uuid == uuid).sort(-c.date).execute(),
                    None)
            if visit:
                visit['time'] = get('t')
                current_app.logger.error(visit['time'])
                visit.save()
            else:
                current_app.logger.error(uuid)
        else:
            return

    def add_geolocalization(self, visit):
        ip = visit['ip']
        lat = None
        lng = None
        country_code = None
        ip = ip.replace('::ffff:', '')
        if ipv4re.match(ip):
            if (ip == '127.0.0.1'
                or ip.startswith('192.168.')
                or ip.startswith('10.')):
                city = 'Local'
                country = 'Local'
            else:
                location = self.gip.record_by_addr(ip)
                city = (location.get('city', 'Unknown')
                        .decode('iso-8859-1')
                        if location else 'Unknown')
                country = (location.get('country_name', 'Unknown')
                        .decode('iso-8859-1')
                        if location else 'Unknown')
                country_code = (location.get('country_code', 'Unknown')
                        .decode('iso-8859-1')
                        if location else 'Unknown')
                lat = location.get('latitude', None)
                lng = location.get('longitude', None)
        else:
            country = 'ipv6'
            city = 'ipv6'
        visit['country'] = country
        visit['country_code'] = country_code
        visit['city'] = city
        visit['lat'] = lat
        visit['lng'] = lng
