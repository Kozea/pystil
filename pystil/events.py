
import pickle
import pika
import gevent
from gevent.event import Event

POLLS = {}


class Poll(object):

    def __init__(self, site):
        self.event = Event()
        self.visits = []

    def get(self, i):
        self.event.wait()
        return self.visits[i:], len(self.visits)

    def add(self, visit):
        self.visits.append(visit)
        self.event.set()
        self.event.clear()


def get_poll(site):
    print 'getting site %s' % site
    if not POLLS.get(site):
        POLLS[site] = Poll(site)
    return POLLS[site]


def init_events(app):
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='pystil_push')

    def callback(ch, method, properties, body):
        from pystil.data.utils import polish_visit
        visit = pickle.loads(body)
        site = visit['host']
        visit = polish_visit(visit)
        poll = get_poll(site)
        poll.add(visit)
        all = get_poll('all')
        all.add(visit)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(callback, queue='pystil_push')
    # Is it good or awful ?
    gevent.spawn(channel.start_consuming)
