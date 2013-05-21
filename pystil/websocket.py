from tornado.websocket import WebSocketHandler
from pystil.context import Hdr, url, MESSAGE_QUEUE


@url(r'/ws')
class PystilWebSocket(Hdr, WebSocketHandler):
    waiters = set()

    def open(self):
        self.log.info('Opening websocket')
        site = self.get_secure_cookie('_pystil_site')
        site = site and site.decode('utf-8').split('|')[0]
        if site is not None:
            self.site = site
            PystilWebSocket.waiters.add(self)
        else:
            self.log.warn('Websocket open without secure cookie')
            self.close()

    def on_message(self, message):
        if message == '/count':
            self.write_message(
                'INFO|There are %d clients' % len(PystilWebSocket.waiters))
        elif message == '/queue_count':
            self.write_message(
                'INFO|There are %d waiting messages' % MESSAGE_QUEUE.qsize())
        elif message == '/site':
            self.write_message(
                'INFO|You are on %s' % self.site)

    def on_close(self):
        if self in PystilWebSocket.waiters:
            PystilWebSocket.waiters.remove(self)


def broadcast(message):
    for client in PystilWebSocket.waiters:
        try:
            client.write_message(message)
        except:
            client.log.exception('Error broadcasting to %r' % client)
            PystilWebSocket.waiters.remove(client)
            client.close()
