#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2011 by Florian Mounier, Kozea
# This file is part of pystil, licensed under a 3-clause BSD license.
"""
pystil - An elegant site web traffic analyzer
"""

import os
import sys
current_dir = os.path.dirname( os.path.abspath( __file__ ) )
pystil_parent_path = os.path.abspath( current_dir + "/.." )
if pystil_parent_path not in sys.path:
    sys.path.append( pystil_parent_path)

from pystil import app, config
import werkzeug.contrib.fixers

config.freeze()

if 'soup' in sys.argv:
    from os import getenv
    from sqlalchemy import create_engine
    from sqlalchemy.ext.sqlsoup import SqlSoup
    import code
    engine = create_engine(config.CONFIG["DB_URL"], echo=True)
    db = SqlSoup(engine)
    Visit = db.visit
    Keys = db.keys

    class FunkyConsole(code.InteractiveConsole):

        def showtraceback(self):
            import pdb
            import sys
            code.InteractiveConsole.showtraceback(self)
            pdb.post_mortem(sys.exc_info()[2])

    console = FunkyConsole(locals=globals())
    if getenv("PYTHONSTARTUP"):
        execfile(getenv("PYTHONSTARTUP"))
    console.interact()
else:
    from pystil.service.http import Application
    from gevent import monkey
    monkey.patch_all()
    import gevent.wsgi
    application = werkzeug.contrib.fixers.ProxyFix(Application(app()))
    ws = gevent.wsgi.WSGIServer(('', 1789), application)
    ws.serve_forever()
