# -*- coding: utf-8 -*-
# Copyright (C) 2011-2013 by Florian Mounier, Kozea
# This file is part of pystil, licensed under a 3-clause BSD license.

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from tornado.web import (
    RequestHandler,
    Application,
    url as unnamed_url)

import logging
from logging.handlers import SysLogHandler, SMTPHandler
from uuid import uuid4
from tornado.options import options
from logging import getLogger
from pystil.db import metadata, Visit
from threading import Thread
from queue import Queue

MESSAGE_QUEUE = Queue()

log = getLogger("pystil")


class Tracking(Thread):
    daemon = True

    def __init__(self, db, log, *args, **kwargs):
        super(Tracking, self).__init__(*args, **kwargs)
        self.log = log
        self.db = db

    def run(self):
        from pystil.websocket import broadcast
        from pystil.utils import visit_to_table_line
        while True:
            try:
                self.log.debug('Blocking for messages')
                message = MESSAGE_QUEUE.get(True)
                self.log.debug('Message got %r' % message)
                try:
                    visit_or_uuid, opening = message.process(self.db)

                    if opening:
                        visit = Visit(**visit_or_uuid)
                        broadcast(
                            'VISIT|' + visit.host + '|' +
                            visit_to_table_line(visit))
                    else:
                        visit_or_uuid and broadcast('EXIT|%s' % visit_or_uuid)
                except:
                    self.log.exception('Error processing visit')
            except:
                self.log.exception('Exception in loop')


class Pystil(Application):
    def listen(self, *args, **kwargs):
        super(Pystil, self).listen(*args, **kwargs)
        db_url = 'postgresql+psycopg2://%s:%s@%s:%d/%s' % (
            options.db_user,
            options.db_password,
            options.db_host,
            options.db_port,
            options.db_name)

        self.db_engine = create_engine(db_url, echo=False)
        metadata.reflect(bind=self.db_engine, schema='agg')
        self.db_metadata = metadata
        self.db = scoped_session(sessionmaker(bind=self.db_engine))
        Tracking(self.db_engine.connect(), self.log).start()
        if not options.debug:
            handler = SysLogHandler(
                address='/dev/log', facility=SysLogHandler.LOG_LOCAL1)
            handler.setLevel(logging.INFO)
            handler.setFormatter(
                logging.Formatter(
                    'PYSTIL: %(name)s: %(levelname)s %(message)s'))

            smtp_handler = SMTPHandler(
                'smtp.keleos.fr',
                'no-reply@pystil.org',
                'pystil-errors@kozea.fr',
                'Pystil Exception')
            smtp_handler.setLevel(logging.ERROR)

            log.addHandler(smtp_handler)
            for logger in (
                    'tornado.access',
                    'tornado.application',
                    'tornado.general',
                    'sqlalchemy'):
                getLogger(logger).addHandler(handler)
                getLogger(logger).addHandler(smtp_handler)
        else:
            self.log.setLevel(logging.DEBUG)
            try:
                from wdb.ext import wdb_tornado, add_w_builtin
            except ImportError:
                pass
            else:
                wdb_tornado(self, start_disabled=True)
                add_w_builtin()

            #getLogger('sqlalchemy').setLevel(logging.DEBUG)

    @property
    def log(self):
        return log


pystil = Pystil(
    debug=options.debug,
    protocol=options.protocol,
    cookie_secret=options.secret,
    static_path=os.path.join(os.path.dirname(__file__), "static"),
    template_path=os.path.join(os.path.dirname(__file__), "templates")
)


class Hdr(RequestHandler):
    @property
    def db(self):
        return self.application.db

    @property
    def log(self):
        return log

    def prepare(self):
        if not self.get_secure_cookie('_pystil_site'):
            self.log.info('Setting secure cookie')
            self.set_secure_cookie('_pystil_site', 'local|' + str(uuid4()))

    def on_finish(self):
        self.db.rollback()


class url(object):
    def __init__(self, url):
        self.url = url

    def __call__(self, cls):
        pystil.add_handlers(
            r'.*$',
            (unnamed_url(self.url, cls, name=cls.__name__),)
        )
        return cls
