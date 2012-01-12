#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
current_dir = os.path.dirname( os.path.abspath( __file__ ) )
pystil_parent_path = os.path.abspath( current_dir + "/.." )
if pystil_parent_path not in sys.path:
    sys.path.append( pystil_parent_path)

from pystil import app, config
import werkzeug.contrib.fixers

config.freeze()

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
