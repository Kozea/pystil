#!/usr/bin/env python2
import pickle
import pika
import threading
from datetime import datetime
from .data import Message
import uuid


with open('pystil/static/pystil.gif') as f:
    gif_content = f.read()

with open('pystil/static/js/pystil.js') as f:
    js_content = f.read()


def application(environ, start_response):
    myapp = threading.local()
    if environ['PATH_INFO'] == '/pystil.js':
        start_response('200 OK', [('Content-Type', 'application/javascript')])
        base_url = 'http://%s/' % environ['HTTP_HOST']
        content = js_content % (str(uuid.uuid4()), base_url)
        return content
    else:
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

if __name__ == '__main__':
    from werkzeug.serving import run_simple
    run_simple('localhost', 12345, application)
