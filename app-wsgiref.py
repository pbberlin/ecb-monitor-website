# https://www.delftstack.com/howto/python-flask/use-a-production-wsgi-server-instead/
# problems installing under windows
# https://docs.python.org/3/library/wsgiref.html
# https://ironpython-test.readthedocs.io/en/latest/library/wsgiref.html

from wsgiref.simple_server import make_server

# from wsgiref.simple_server import WSGIServer
# from wsgiref.simple_server import WSGIRequestHandler
from wsgiref.handlers      import BaseHandler
from wsgiref.util          import setup_testing_defaults


def WebApp(environ, response):
    status = "200 OK"        
    headers = [("content-type", "text/html; charset=utf-8")]
    response(status, headers)

    if False:
        setup_testing_defaults(environ)

    ret = [b"<h2>This is WSGI server</h2>"]

    for key, val in environ.items():
        if len(key)>4:
            prefix = key[0:5]
            if prefix == "wsgi.":
                ret += [("%s: %s  <br>\n" % (key, val)).encode("utf-8")]


    return ret


if __name__ == '__main__':
    BaseHandler.wsgi_multiprocess = True
    BaseHandler.wsgi_multithread  = True
    #  this should set the number of workers to something other than 1, but does not

    with make_server("", 5000, WebApp) as server:
        print(
            "serving on port 5000...\nvisit http://127.0.0.1:5000\nTo exit press ctrl + c"
        )
        server.serve_forever()

