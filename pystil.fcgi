#!/usr/bin/python
from flup.server.fcgi import WSGIServer
from pystil import app
import os

ipdb = os.path.join(os.path.dirname(__file__), 'ip.db')
WSGIServer(app(ipdb=ipdb), debug=False).run()
