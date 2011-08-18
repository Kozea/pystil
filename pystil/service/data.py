import urlparse
from datetime import datetime
from werkzeug.useragents import UserAgent
from multicorn.requests import CONTEXT as c
from pygeoip import GeoIP, MMAP_CACHE
import threading
import re

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
        request_args = urlparse.parse_qs(self.query)
        kind = request_args.get('d', [None])[0]
        uuid = request_args.get('_', [None])[0]
        user_agent = UserAgent(self.user_agent)
        if kind == 'o':
            last_visit = request_args.get('l', [None])[0]
            if last_visit:
                last_visit = datetime.fromtimestamp(int(last_visit) / 1000)
            visit = {}
            visit['uuid'] = uuid
            visit['host'] = request_args.get('k', [None])[0]
            visit['site'] = request_args.get('u', [None])[0]
            visit['client_tz_offset'] = request_args.get('z', [0])[0]
            visit['date'] = datetime.now()
            visit['last_visit'] = last_visit
            visit['ip'] = self.remote_addr
            visit['referrer'] = request_args.get('r', [None])[0]
            visit['size'] = request_args.get('s', [None])[0]
            visit['page'] = request_args.get('p', [None])[0]
            visit['hash'] = request_args.get('h', [None])[0]
            visit['query'] = request_args.get('q', [None])[0]
            visit['browser_name'] = user_agent.browser
            visit['browser_version'] = user_agent.version
            visit['platform'] = user_agent.platform
            visit['language'] = user_agent.language
            visit = Visit.create(visit)
            visit.save()
        elif kind == 'c':
            visit = next(Visit.all.filter(c.uuid == uuid).sort(-c.date).execute(),
                    None)
            if visit:
                visit['time'] = request_args.get('t', [None])[0]
                visit.save()
        else:
            return

    def add_geolocalization(self, visit):
        ip = visit['ip']
        lat = None
        lng = None
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
                lat = location.get('latitude', None)
                lng = location.get('longitude', None)
        else:
            country = 'ipv6'
            city = 'ipv6'
        visit['country'] = country
        visit['city'] = city
        visit['lat'] = lat
        visit['lng'] = lng

