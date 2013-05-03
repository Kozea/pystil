from tornado.ioloop import IOLoop
from tornado.options import options, parse_command_line
from subprocess import call
from pystil.context import pystil


parse_command_line()
pystil.listen(options.port)
if options.debug:
    try:
        call("wsreload --url 'http://l:1789/*'", shell=True)
    except:
        pass

IOLoop.instance().start()
