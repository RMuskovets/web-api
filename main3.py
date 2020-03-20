from flask import *
from flask_httpauth import *

app = Flask(__name__)
auth = HTTPBasicAuth()

@auth.verify_password
def check_pass(nm, pw):
    for l in open('data.txt', 'r').readlines():
        if nm == l.strip().split(':')[0].strip()\
        and pw== l.strip().split(':')[1].strip():
            return True
    return False

def header_auth():
    if 'auth' in request.args and request.args['auth']:
        auth = request.args['auth']
        if ':' in auth:
            if check_pass(auth.split(':')[0], auth.split(':')[1]):
                return True
        elif '%3A' in auth:
            if check_pass(auth.split('%3A')[0], auth.split('%3A')[1]):
                return True
    return False

def post_auth():
    if 'auth' in request.form and request.form['auth']:
        auth = request.form['auth']
        if ':' in auth:
            if check_pass(auth.split(':')[0], auth.split(':')[1]):
                return True
        elif '%3A' in auth:
            if check_pass(auth.split('%3A')[0], auth.split('%3A')[1]):
                return True
    return False

@app.route('/api/show')
@auth.login_required
def get():
    if not header_auth():
        return '{"error":"auth-GET"}'
    l = []
    for l_ in open('data.txt', 'r').readlines():
        if ':' in l_:
            n, p = l_.split(':')
            n, p = n.strip(), p.strip()
            l.append(f'"{n}":"{p}"')
    return '{' + ','.join(l) + '}'

@app.route('/api/add', methods=['POST'])
@auth.login_required
def post():
    if not header_auth():
        return '{"error":"auth-GET"}'
    if not post_auth():
        return '{"error":"auth-POST"}'
    post = request.form
    nm, pw = post['username'], post['password']
    l = f'{nm}:{pw}\n'
    with open('data.txt', 'a') as f:
        f.write(l)
        f.flush()
    return '{"error":null}'

@app.route('/api/delete', methods=['POST'])
@auth.login_required
def delete():
    if not header_auth():
        return '{"error":"auth-GET"}'
    if not post_auth():
        return '{"error":"auth-POST"}'
    post = request.form
    nm = post['username']
    ls = open('data.txt', 'r').readlines()
    nls = []
    deleted = False
    for l in ls:
        if not l.startswith(nm):
            nls.append(l)
        else:
            deleted = True
    nls = list(filter(lambda x: bool(x.strip()), nls))
    print(nls)
    with open('data.txt', 'w') as f:
        f.write(''.join(nls))
        f.flush()
    return '{"error":null}' if deleted else '{"error":"not-found"}'

@app.route('/ui.html')
def uihtml():
    return open('docs/index.html').read()

@app.route('/spec.js')
def specjs():
    return open('docs/spec.js').read()

@app.errorhandler(401)
def on401():
    return '{"error":"auth-HTTP"}'

app.run('', 8888)
