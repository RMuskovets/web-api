from server2 import WebServer

srv = WebServer(
    '',
    8888
)

def get(_):
    l = []
    for l_ in open('data.txt', 'r').readlines():
        n, p = l_.split(':')
        n, p = n.strip(), p.strip()
        l.append(f'"{n}":"{p}"')
    return '{' + ','.join(l) + '}'

def post(inp):
    post = inp['bodyparams']
    nm, pw = post['username'], post['password']
    l = f'{nm}:{pw}\n'
    with open('data.txt', 'a') as f:
        f.write(l)
        f.flush()
    return 'ok'

def delete(inp):
    post = inp['bodyparams']
    nm = post['username']
    ls = open('data.txt', 'r').readlines()
    nls = []
    for l in ls:
        if not l.startswith(nm):
            nls.append(l)
    with open('data.txt', 'w') as f:
        f.write('\n'.join(nls))
        f.flush()
    return 'ok'

srv.get('/api/show', get)
srv.post('/api/add', post)
srv.post('/api/del', delete)

srv.run()