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
from tornado.options import options
from logging import getLogger
from pystil.db import metadata, Visit
from threading import Thread
from queue import Queue

MESSAGE_QUEUE = Queue()

log = getLogger("pystil")


def monkey_patch():
    old_execute = RequestHandler._execute

    def _wdb_execute(self, transforms, *args, **kwargs):
        from wdb import Wdb
        wdbr = Wdb.trace()
        old_execute(self, transforms, *args, **kwargs)
        wdbr.stop_trace()
        wdbr.die()

    RequestHandler._execute = _wdb_execute

# monkey_patch()


class Tracking(Thread):
    def __init__(self, db, log, *args, **kwargs):
        super(Tracking, self).__init__(*args, **kwargs)
        self.log = log
        self.db = db

    def run(self):
        from pystil.websocket import broadcast
        from pystil.utils import visit_to_table_line
        while True:
            try:
                self.log.info('Blocking for messages')
                message = MESSAGE_QUEUE.get(True)
                self.log.info('Message got %r' % message)
                try:
                    visit_or_uuid, opening = message.process(self.db)

                    if opening:
                        broadcast(
                            'VISIT|' + visit_to_table_line(
                                Visit(**visit_or_uuid)))
                    else:
                        visit_or_uuid and broadcast('EXIT|%s' % visit_or_uuid)
                except:
                    self.log.exception('Error processing visit')
            except:
                self.log.exception('Exception in loop')


class Pystil(Application):
    def __init__(self, *args, **kwargs):
        super(Pystil, self).__init__(*args, **kwargs)
        db_url = 'postgresql+psycopg2://%s:%s@%s:%d/%s' % (
            options.db_user,
            options.db_password,
            options.db_host,
            options.db_port,
            options.db_name)

        self.db_engine = create_engine(db_url, echo=False)
        self.db_metadata = metadata
        self.db = scoped_session(sessionmaker(bind=self.db_engine))
        Tracking(self.db_engine.connect(), self.log).start()
        # getLogger('sqlalchemy').setLevel(10)
        # getLogger('sqlalchemy').setLevel(10)

    @property
    def log(self):
        return log


pystil = Pystil(
    debug=options.debug,
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


class url(object):
    def __init__(self, url):
        self.url = url

    def __call__(self, cls):
        pystil.add_handlers(
            r'.*$',
            (unnamed_url(self.url, cls, name=cls.__name__),)
        )
        return cls
