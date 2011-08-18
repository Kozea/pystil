#!/usr/bin/env python2
import pika
import pickle
from pystil import config

if __name__ == '__main__':
    config.freeze()
    connection = pika.BlockingConnection(pika.ConnectionParameters(
        host='localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='pystil')

    def callback(ch, method, properties, body):
        message = pickle.loads(body)
        message.process()
    channel.basic_consume(callback, queue='pystil', no_ack=True)
    channel.start_consuming()
