#!/usr/bin/env python
from pystil import app, config
import werkzeug.contrib.fixers
import os

config.CONFIG["SECRETS_FILE"] = (
    '/var/www/.%s-secrets' % config.CONFIG["PYSTIL_INSTANCE"])
config.CONFIG["DEBUG"] = False
config.CONFIG["TESTING"] = False
config.CONFIG["IP_DB"] = os.path.join(os.path.dirname(__file__), 'ip.db')
config.CONFIG["LOG_FILE"] = (
    '/var/log/lighttpd/%s.log' % config.CONFIG["PYSTIL_INSTANCE"])
config.freeze()

from pystil.service.http import Application
from gevent import monkey
monkey.patch_all()
import gevent.wsgi
application = werkzeug.contrib.fixers.ProxyFix(Application(app()))
ws = gevent.wsgi.WSGIServer(('', config.CONFIG['PORT']), application)
ws.serve_forever()
