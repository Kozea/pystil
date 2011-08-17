import urlparse
from datetime import datetime
from werkzeug.useragents import UserAgent
from multicorn.requests import CONTEXT as c

class Message(object):

    def __init__(self, query, user_agent, remote_addr):
        self.query = query
        self.stamp = datetime.now()
        self.user_agent = user_agent
        self.remote_addr = remote_addr

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
