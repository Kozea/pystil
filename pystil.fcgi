#!/usr/bin/python
from flup.server.fcgi import WSGIServer
from pystil import app

WSGIServer(app(), debug=False).run()
