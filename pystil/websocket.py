from tornado.websocket import WebSocketHandler
from pystil.context import url, MESSAGE_QUEUE, log, Hdr
from pystil.db import CriterionView as Visit
from tornado.options import options
from tornado.ioloop import IOLoop
from psycopg2.extensions import POLL_OK, POLL_READ, POLL_WRITE
from sqlalchemy.sql.compiler import SQLCompiler
from sqlalchemy.sql.expression import between
from pystil.utils import visit_to_table_line
from sqlalchemy import func
from datetime import datetime, timedelta
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
            log.warn('Last visits websocket open without secure cookie')
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
        self.paused = True
        if site is None:
            log.warn('Query websocket open without secure cookie')
            self.close()
            return

    def on_message(self, message):
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
                filter_ = between(Visit.date,
                                  value.date(),
                                  value.date() + timedelta(days=1))
            elif criterion in (
                    'referrer', 'asn', 'browser_name', 'site',
                    'browser_version', 'browser_name_version', 'query'):
                filter_ = getattr(Visit, criterion).ilike('%%%s%%' % value)
            else:
                filter_ = func.lower(
                    getattr(Visit, criterion)) == value.lower()

            query = (self.db
                     .query(Visit)
                     .filter(filter_))
            dialect = query.session.bind.dialect
            compiler = SQLCompiler(dialect, query.statement)
            compiler.compile()
            self.count = 0
            self.stop = 20
            self.start = True
            self.execute(compiler.string, compiler.params)
        elif command == 'more':
            if self.paused:
                self.stop += 20
                self.paused = False
                self.cursor.execute(
                    'FETCH FORWARD 1 FROM visit_cur;')
        elif command == '/status':
            for i, conn in enumerate(adb._pool):
                if conn.busy():
                    self.write_message(
                        'INFO|Connection %d is busy: '
                        'Executing? %s Closed? %d Status? %s' % (
                            i, conn.connection.isexecuting(),
                            conn.connection.closed,
                            conn.connection.get_transaction_status()))
                else:
                    self.write_message('INFO|Connection %d is free' % i)

    def execute(self, query, parameters):
            self.terminated = False
            self.momoko_connection = adb._get_connection()
            if not self.momoko_connection:
                if self.start:
                    log.info('No connection')
                    self.write_message('BUSY|Server busy, waiting for slot')
                self.start = False
                if self.ws_connection:
                    return adb._ioloop.add_callback(partial(
                        self.execute, query, parameters))
            if not self.ws_connection:
                return
            self.start = True
            self.write_message('BEGIN|Searching')
            self.paused = False
            self.connection = self.momoko_connection.connection
            self.cursor = self.connection.cursor(
                cursor_factory=psycopg2.extras.NamedTupleCursor)
            self.cursor.execute(
                'BEGIN;'
                'DECLARE visit_cur SCROLL CURSOR FOR '
                '%s;'
                'SELECT null as id;' % query, parameters)
                # 'FETCH FORWARD 1 FROM visit_cur;' % query, parameters)
            self.momoko_connection.ioloop.add_handler(
                self.momoko_connection.fileno,
                self.io_callback,
                IOLoop.WRITE)

    def io_callback(self, fd=None, events=None):
        try:
            state = self.connection.poll()
        except psycopg2.extensions.QueryCanceledError:
            log.info('Canceling request %r' % self, exc_info=True)
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
                try:
                    rows = self.cursor.fetchmany()
                except:
                    self.connection.cancel()
                    self.momoko_connection.ioloop.remove_handler(
                        self.momoko_connection.fileno)
                    return

                if not rows:
                    self.terminated = True
                    self.cursor.execute('CLOSE visit_cur; ROLLBACK;')
                    try:
                        self.write_message('END|Done found %d visit%s' % (
                            self.count, 's' if self.count > 1 else ''))
                    except:
                        pass
                else:
                    try:
                        for row in rows:
                            if row.id:
                                self.count += 1
                                self.write_message(
                                    'VISIT|' + visit_to_table_line(row))
                    except Exception as e:
                        log.warn('During write', exc_info=True)
                        self.terminated = True
                        self.cursor.execute('CLOSE visit_cur; ROLLBACK;')
                        try:
                            self.write_message(
                                'END|%s: %s' % (type(e), str(e)))
                        except:
                            pass
                    else:
                        if self.count < self.stop:
                            self.cursor.execute(
                                'FETCH FORWARD 1 FROM visit_cur;')
                        else:
                            self.paused = True
                            try:
                                self.write_message(
                                    'PAUSE|Paused on %d visits' % self.count)
                            except:
                                pass
            elif state == POLL_READ:
                self.momoko_connection.ioloop.update_handler(
                    self.momoko_connection.fileno, IOLoop.READ)
            elif state == POLL_WRITE:
                self.momoko_connection.ioloop.update_handler(
                    self.momoko_connection.fileno, IOLoop.WRITE)
            else:
                raise psycopg2.OperationalError(
                    'poll() returned {0}'.format(state))

    def on_close(self):
        log.info('Closing %r' % self)
        if not self.start:
            return
        if self.paused:
            self.cursor.execute('CLOSE visit_cur; ROLLBACK;')
        self.connection.cancel()
