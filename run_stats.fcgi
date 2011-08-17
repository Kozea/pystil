from pystil.service.http import application

from flup.server.fcgi import WSGIServer

if __name__ == '__main__':
    WSGIServer(application, debug=False).run()
