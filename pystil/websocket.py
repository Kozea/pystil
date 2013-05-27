from tornado.websocket import WebSocketHandler
from pystil.context import url, MESSAGE_QUEUE, log, Hdr
from pystil.db import Visit
from tornado.options import options
from tornado.ioloop import IOLoop
from psycopg2.extensions import POLL_OK, POLL_READ, POLL_WRITE
from sqlalchemy.sql.compiler import SQLCompiler
from pystil.utils import visit_to_table_line
from sqlalchemy import func, desc
from datetime import datetime
from functools import partial
import psycopg2
import momoko


dsn = 'dbname=%s user=%s password=%s host=%s port=%s' % (
    options.db_name, options.db_user, options.db_password,
    options.db_host, options.db_port)

adb = momoko.Pool(dsn=dsn, size=5)


@url(r'/last_visits')
class LastVisitsWebSocket(WebSocketHandler):
    waiters = set()

    def open(self):
        log.info('Opening last visits websocket')
        site = self.get_secure_cookie('_pystil_site')
        site = site and site.decode('utf-8').split('|')[0]
        if site is not None:
            self.site = site
            LastVisitsWebSocket.waiters.add(self)
        else:
            log.warn('Lats visits websocket open without secure cookie')
            self.close()

    def on_message(self, message):
        if message == '/count':
            self.write_message(
                'INFO|There are %d clients' % len(LastVisitsWebSocket.waiters))
        elif message == '/queue_count':
            self.write_message(
                'INFO|There are %d waiting messages' % MESSAGE_QUEUE.qsize())
        elif message == '/site':
            self.write_message(
                'INFO|You are on %s' % self.site)

    def on_close(self):
        if self in LastVisitsWebSocket.waiters:
            LastVisitsWebSocket.waiters.remove(self)


def broadcast(message):
    for client in set(LastVisitsWebSocket.waiters):
        try:
            client.write_message(message)
        except:
            client.log.exception('Error broadcasting to %r' % client)
            LastVisitsWebSocket.waiters.remove(client)
            client.close()


@url(r'/query')
class QueryWebSocket(Hdr, WebSocketHandler):

    def open(self):
        log.info('Opening query websocket')
        site = self.get_secure_cookie('_pystil_site')
        site = site and site.decode('utf-8').split('|')[0]
        self.query = None
        if site is None:
            log.warn('Query websocket open without secure cookie')
            self.close()
            return

    def on_message(self, message):
        log.warn('Message from %r' % self)
        command = message.split('|')[0]
        query = '|'.join(message.split('|')[1:])
        if command == 'criterion':
            criterion = query.split('|')[0]
            value = '|'.join(query.split('|')[1:])
            if criterion == 'date':
                try:
                    value = datetime.strptime(
                        value.replace('+', ' '), '%Y-%m-%d %H:%M:%S')
                except ValueError:
                    try:
                        value = datetime.strptime('%Y-%m-%d')
                    except ValueError:
                        value = datetime.now()
                filter_ = func.date_trunc('DAY', Visit.date) == value.date()
            elif criterion in (
                    'referrer', 'asn', 'browser_name', 'site',
                    'browser_version', 'browser_name_version', 'query'):
                filter_ = getattr(Visit, criterion).ilike('%%%s%%' % value)
            else:
                filter_ = func.lower(
                    getattr(Visit, criterion)) == value.lower()

            query = (self.db
                     .query(Visit)
                     .filter(filter_)
                     .order_by(desc(Visit.date))
                     .limit(20))
            dialect = query.session.bind.dialect
            compiler = SQLCompiler(dialect, query.statement)
            compiler.compile()
            self.execute(compiler.string, compiler.params)

    def execute(self, query, parameters):
            self.terminated = False
            self.momoko_connection = adb._get_connection()
            if not self.momoko_connection:
                log.warn('No connection')
                return adb._ioloop.add_callback(partial(self.execute, query))
            self.connection = self.momoko_connection.connection

            self.cursor = self.connection.cursor(
                cursor_factory=psycopg2.extras.NamedTupleCursor)
            self.cursor.execute(
                'BEGIN;'
                'DECLARE visit_cur SCROLL CURSOR FOR '
                '%s;'
                'FETCH FORWARD 1 FROM visit_cur;' % query, parameters)
            self.momoko_connection.ioloop.add_handler(
                self.momoko_connection.fileno,
                self.io_callback,
                IOLoop.WRITE)

    def io_callback(self, fd=None, events=None):
        try:
            state = self.connection.poll()
        except psycopg2.extensions.QueryCanceledError:
            log.warn('Canceling request %r' % self, exc_info=True)
            self.cursor.execute('ROLLBACK')
            self.terminated = True
        except (psycopg2.Warning, psycopg2.Error):
            log.exception('Poll error')
            self.momoko_connection.ioloop.remove_handler(
                self.momoko_connection.fileno)
            raise
        else:
            if state == POLL_OK:
                if self.terminated:
                    self.momoko_connection.ioloop.remove_handler(
                        self.momoko_connection.fileno)
                    return
                rows = self.cursor.fetchmany()
                if not rows:
                    self.terminated = True
                    self.cursor.execute('CLOSE visit_cur; ROLLBACK;')
                else:
                    try:
                        for row in rows:
                            self.write_message(
                                'VISIT|' + visit_to_table_line(row))
                    except:
                        log.exception('During write')
                        self.terminated = True
                        self.cursor.execute('CLOSE visit_cur; ROLLBACK;')
                    else:
                        self.cursor.execute('FETCH FORWARD 1 FROM visit_cur;')
            elif state == POLL_READ:
                self.momoko_connection.ioloop.update_handler(
                    self.momoko_connection.fileno, IOLoop.READ)
            elif state == POLL_WRITE:
                self.momoko_connection.ioloop.update_handler(
                    self.momoko_connection.fileno, IOLoop.WRITE)
            else:
                raise psycopg2.OperationalError(
                    'poll() returned {0}'.format(state))

    # self.write_message('VISIT|' + visit_to_table_line(next(self.query)))

    def on_close(self):
        log.warn('Closing %r' % self)
        self.connection.cancel()
