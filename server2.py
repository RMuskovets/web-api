from socket import socket, SOCK_STREAM, AF_INET, SOL_SOCKET, SO_REUSEADDR
import re


def get_method(lines):
    return lines[0].split(' ')[0]


def get_uri(lines):
    return lines[0].split(' ')[1]


class WebServer(object):
    def __init__(self, url, port, max_conn=10, threads=2):
        print(f'Start init')
        self.addr = url, port
        self.fns = {}
        self.maxconn = max_conn
        self.threads = threads
        print(f'Init success (url={url} port={port} maxconn={max_conn} threads={threads})')

    def _add(self, method, uri, fn):
        print(f'Start _add (method={method} uri={uri})')
        if uri in self.fns:
            print(f'{uri} in {self.fns} = true')
            if method in self.fns[uri].keys():
                raise Exception()
            print(f'{method} not in {self.fns.keys()}')
            self.fns[uri][method.lower()] = fn
        print(f'{uri} not in {self.fns}')
        print(f'Adding {uri} ({method}) to registry')
        self.fns[uri] = {method.lower(): fn}
        print(f'_add success (uri={uri} method={method})')

    def get(self, uri, fn):
        print(f'Start get (uri={uri})')
        self._add('get', uri, fn)
        print('End get')

    def post(self, uri, fn):
        print(f'Start post (uri={uri})')
        self._add('post', uri, fn)
        print('End post')

    def run(self):
        print('Start running')
        listener = socket(AF_INET, SOCK_STREAM)
        print('Init socket OK')
        listener.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        print('Setsockopt OK')
        listener.bind(self.addr)
        print(f'Bind to {self.addr[0]}:{self.addr[1]} OK')
        listener.listen(self.maxconn)
        print(f'Listen to {self.maxconn} connections OK')

        def onrequest(conn):
            chunks = []
            chunksz = 4096
            while 1:
                read = conn.recv(chunksz)
                print('Read chunk: ' + read.decode('utf-8'))
                chunks.append(read.decode('utf-8'))
                if read != chunksz:
                    break
            data = ''.join(chunks)

            method = get_method(data.split('\n'))
            print(f'HTTP Method: {method}')
            requri = get_uri(data.split('\n'))
            print(f'requri: {requri}')

            found = False

            for uri in self.fns.keys():
                print(f'Checking {uri}')
                uri_re = re.sub(r':[^/]+', r'([^/]+)', re.escape(uri)) + r'\??.*'
                print(f'URI regex: {uri_re}')
                match = re.search(uri_re, requri)
                if match:
                    print(f'URL check OK; checking methods')
                    print(match.groups())
                    if method.lower() in self.fns[uri].keys():
                        print(f'Method check OK')
                        found = True
                        urlparams = list(match.groups())
                        print(f'L85 ok {urlparams}')
                        getparams = {}
                        try:
                            qmindex = requri.index('?')
                        except:
                            qmindex = -1
                        print(f'qmindex = {qmindex}')
                        if qmindex != -1:
                            print('qmindex != -1')
                            parstrng = requri[qmindex+1:]
                            for s in parstrng.split('&'):
                                getparams[s.split('=')[0]] = s.split('=')[1]
                        else:
                            print('qmindex == -1')
                        if method.lower() == 'post':
                            bodyparams = {}
                            pass
                        else:
                            bodyparams = {}
                        print(f'Data to send: {requri} {urlparams} {getparams}')
                        resp = self.fns[uri][method.lower()]({
                            'url': requri,
                            'urlparams': urlparams,
                            'getparams': getparams,
                            'bodyparams': bodyparams
                        })
                        print(f'Response: {resp}')
                        conn.sendall(b'HTTP/1.1 200 OK\n\n' + resp.encode('utf-8'))
                        break
            if not found:
                conn.sendall(b'HTTP 1.1 404 Not Found\n\n')

        stop = False

        def serve():
            while not stop:
                try:
                    client, _ = listener.accept()
                    print('client accepted')
                    if client is None:
                        continue
                    print('client not None')
                    onrequest(client)
                    print('request processed')
                except Exception as e:
                    print('exception')
                    print(e)

        serve()
