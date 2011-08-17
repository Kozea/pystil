#!/usr/bin/env python2
import pika
import pickle
import urlparse
from datetime import datetime
from werkzeug.useragents import UserAgent
from pystil import config

if __name__ == '__main__':
    config.freeze()
    from pystil.corns import Visit
    from multicorn.requests import CONTEXT as c
    connection = pika.BlockingConnection(pika.ConnectionParameters(
        host='localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='pystil')
    def callback(ch, method, properties, body):
        message = pickle.loads(body)
        request_args = urlparse.parse_qs(message.query)
        kind = request_args.get('d', [None])[0]
        uuid = request_args.get('_', [None])[0]
        user_agent = UserAgent(message.user_agent)
        print uuid
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
            visit['ip'] = message.remote_addr
            visit['referrer'] = request_args.get('r', [None])[0]
            visit['size'] = request_args.get('s', [None])[0]
            visit['page'] = request_args.get('p', [None])[0]
            visit['hash'] = request_args.get('h', [None])[0]
            visit['query'] = request_args.get('q', [None])[0]
            visit['browser_name'] = user_agent.browser
            visit['browser_version'] = user_agent.version
            visit['platform'] = user_agent.platform
            visit['language'] = user_agent.language
            print "New visit!"
            visit = Visit.create(visit)
            visit.save()
        elif kind == 'c':
            visit = Visit.all.filter(c.uuid == uuid).one(None).execute()
            if visit:
                visit['time'] = request_args.get('t', [None])[0]
                visit.save()
                print "Ending visit!"
        else:
            return
    channel.basic_consume(callback, queue='pystil')
    channel.start_consuming()
