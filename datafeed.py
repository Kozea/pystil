#!/usr/bin/env python
import os
import sys
import pika
import pickle
from pystil import config

if __name__ == '__main__':
    # sys.stdout = open(os.devnull, "w")
    # sys.stderr = open("/var/log/pystil.err", "w")

    config.freeze()
    connection = pika.BlockingConnection(pika.ConnectionParameters(
        host='localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='pystil')
    channel.exchange_declare(exchange='pystil', type='fanout')
    channel.queue_bind(exchange='pystil', queue='pystil')

    def callback(ch, method, properties, body):
        print 'Got'
        message = pickle.loads(body)
        message.process()
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(callback, queue='pystil')
    channel.start_consuming()
