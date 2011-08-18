#!/usr/bin/python
from flup.server.fcgi import WSGIServer
from pystil.service.http import Application
from pystil import app, config
import os

config.CONFIG["SECRETS_FILE"] = '/var/www/.pystil-secrets'
config.CONFIG["DEBUG"] = False
config.CONFIG["TESTING"] = False
config.CONFIG["IP_DB"] = os.path.join(os.path.dirname(__file__), 'ip.db')
config.CONFIG["LOG_FILE"] = '/var/log/lighttpd/pystil.log'
config.freeze()
if config.CONFIG["PUBLIC_ROUTES"]:
    wsgi = app()
else:
    wsgi = Application(app())
WSGIServer(wsgi, debug=False).run()
