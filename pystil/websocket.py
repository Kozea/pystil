from tornado.websocket import WebSocketHandler
from pystil.context import Hdr, url, MESSAGE_QUEUE


CLIENTS = []


@url(r'/ws')
class EchoWebSocket(Hdr, WebSocketHandler):

    def open(self):
        self.log.info('Opening websocket')
        CLIENTS.append(self)

    def on_message(self, message):
        if message == '/count':
            self.write_message('INFO|There are %d clients' % len(CLIENTS))
        elif message == '/queue_count':
            self.write_message(
                'INFO|There are %d waiting messages' % MESSAGE_QUEUE.qsize())

    def on_close(self):
        CLIENTS.remove(self)


def broadcast(message):
    for client in CLIENTS:
        try:
            client.write_message(message)
        except:
            client.log.exception('Error broadcasting to %r' % client)
            CLIENTS.remove(client)
