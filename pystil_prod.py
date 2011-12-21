#!/usr/bin/python
from pystil import app, config
import werkzeug.contrib.fixers
import os


config.CONFIG["SECRETS_FILE"] = '/var/www/.pystil-secrets'
config.CONFIG["DEBUG"] = False
config.CONFIG["TESTING"] = False
config.CONFIG["IP_DB"] = os.path.join(os.path.dirname(__file__), 'ip.db')
config.CONFIG["LOG_FILE"] = '/var/log/lighttpd/pystil.log'
config.freeze()

from pystil.service.http import Application
from gevent import monkey
monkey.patch_all()
import gevent.wsgi
application = werkzeug.contrib.fixers.ProxyFix(Application(app()))
ws = gevent.wsgi.WSGIServer(('', 1789), application)
ws.serve_forever()
