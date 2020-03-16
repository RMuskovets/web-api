from http.server import *

def run(handler_class, server_class=HTTPServer):
    server_address = ('', 8888)
    httpd = server_class(server_address, handler_class)
    httpd.serve_forever()

