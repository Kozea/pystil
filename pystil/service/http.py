#!/usr/bin/env python2
import pickle
import pika
import threading
import re
from .data import Message
import uuid


with open('pystil/static/pystil.gif') as f:
    gif_content = f.read()

with open('pystil/static/js/pystil.js') as f:
    js_content = f.read()

def render_js(environ):
    base_url = 'http://%s/' % environ['HTTP_HOST']
    content = js_content % (str(uuid.uuid4()), base_url)
    return content


class Application(object):

    def __init__(self, delegate=lambda x, y: None):
        self.delegate = delegate

    def __call__(self, environ, start_response):
        myapp = threading.local()
        if environ['PATH_INFO'] == '/pystil.js':
            start_response('200 OK', [('Content-Type', 'application/javascript')])
            return render_js(environ)
        elif re.match('/pystil-[^/]*\.gif', environ['PATH_INFO']):
            start_response('200 OK', [('Content-Type', 'image/gif')])
            if not hasattr(myapp, 'connection'):
                params  = pika.ConnectionParameters(host='localhost')
                myapp.connection = pika.BlockingConnection(params)
                myapp.channel = myapp.connection.channel()
                myapp.channel.queue_declare(queue='pystil')
            message = Message(environ['QUERY_STRING'], environ['HTTP_USER_AGENT'],
                    environ['REMOTE_ADDR'])
            myapp.channel.basic_publish(exchange='',
                routing_key='pystil',
                body=pickle.dumps(message))
            return gif_content
        else:
            return self.delegate(environ, start_response)
