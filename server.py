from socket import *
from threading import Thread
from typing import *

def get_path_from_http_request(method, req):
    first_line = req.decode('utf-8').splitlines()[0]
    if '?' not in first_line:
        http_index = first_line.index(' HTTP')
    else:
        http_index = first_line.index('?')
    get_index = first_line.index(f'{method} ') + 4
    return first_line[get_index:http_index]


def path_matches(path, uri):
    return path == uri


def get_method(uri):
    pass

class WebServer:

    def __init__(self, port: int = 8888, threads: int = 5, address: str = '', debug: bool = False):
        self.functions: Dict = {}
        self.middlewares: List = []
        self.port: int = port
        self.thread_count: int = threads
        self.address: str = address
        self.debug: bool = debug

    def bind(self, func, name):
        self.functions['/' + name] = func

    def middle(self, fn):
        self.middlewares.append(fn)

    def run(self):
        listen_socket = socket(AF_INET, SOCK_STREAM)
        listen_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        listen_socket.bind((self.address, self.port))
        listen_socket.listen(self.thread_count)

        def handle_request(conn):
            request = conn.recv(1024)
            method = get_method(request)
            uri = get_path_from_http_request(method, request)
            text = b'HTTP/1.1 404 Not Found\n\nNot Found'
            for path in self.functions:
                if path_matches(path, uri):
                    func = self.functions[path]
                    fnres = func()
                    for m in self.middlewares:
                        fnres = m(fnres)
                    text = b'HTTP/1.1 200 OK\n\n' + fnres.encode('utf-8')
            conn.sendall(text)

        def serve():
            needs_to_stop = 0
            while not needs_to_stop:
                client, _ = listen_socket.accept()
                handle_request(client)
                client.close()

        for i in range(self.thread_count):
            Thread(target=serve).start()


__all__ = ['WebServer']
