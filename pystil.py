#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2011 by Florian Mounier, Kozea
# This file is part of pystil, licensed under a 3-clause BSD license.
"""
pystil - An elegant site web traffic analyzer
"""
from pystil import app, config
import sys

config.freeze()

if 'shell' in sys.argv:
    from os import getenv
    from sqlalchemy.ext.sqlsoup import SqlSoup
    import code
    db = SqlSoup(config.CONFIG["DB_URL"])
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
elif 'rabbit' in sys.argv:
    print "Developping with a rabbit"
    from werkzeug.serving import run_simple
    from pystil.service.http import Application
    run_simple('0.0.0.0', 12345, Application(app()),
            use_reloader=True, use_debugger=True)
else:
    app().run(host='0.0.0.0', port=12345, debug=True)
