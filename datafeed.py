#!/usr/bin/env python2
import os
import sys
import pika
import pickle
from pystil import config

if __name__ == '__main__':
    sys.stdout = open(os.devnull, "w")
    sys.stderr = open("/var/log/pystil.err", "w")

    config.freeze()
    connection = pika.BlockingConnection(pika.ConnectionParameters(
        host='localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='pystil')

    def callback(ch, method, properties, body):
        message = pickle.loads(body)
        message.process()
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(callback, queue='pystil')
    channel.start_consuming()
