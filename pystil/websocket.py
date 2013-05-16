from tornado.websocket import WebSocketHandler
from pystil.context import Hdr, url


CLIENTS = []


@url(r'/ws')
class EchoWebSocket(Hdr, WebSocketHandler):

    def open(self):
        CLIENTS.append(self)

    def on_message(self, message):
        if message == '/count':
            self.write_message('INFO|There are %d clients' % len(CLIENTS))

    def on_close(self):
        CLIENTS.remove(self)


def broadcast(message):
    for client in CLIENTS:
        try:
            client.write_message(message)
        except:
            client.log.exception('Error broadcasting to %r' % client)
            CLIENTS.remove(client)
