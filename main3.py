from flask import *
from flask_httpauth import *

app = Flask(__name__)
auth = HTTPBasicAuth()

@auth.verify_password
def check_pass(nm, pw):
    # авторизація по хеадеру
    for l in open('data.txt', 'r').readlines():
        if nm == l.strip().split(':')[0].strip()\
        and pw== l.strip().split(':')[1].strip():
            return True
    return False

def auth_in_url():
    # авторизація для ГЕТ запитів (по УРЛ)
    if request.args['auth']:
        auth = request.args['auth']
        if ':' in auth:
            if check_pass(auth.split(':')[0], auth.split(':')[1]):
                return True
    return False

def post_auth():
    # авторизація через БОДІ запиту
    if request.form['auth']:
        auth = request.form['auth']
        if ':' in auth:
            if check_pass(auth.split(':')[0], auth.split(':')[1]):
                return True
    return False

@app.route('/api/show')
@auth.login_required
def get():
    if not auth_in_url():
        return '{"error":"auth"}'
    l = []
    for l_ in open('data.txt', 'r').readlines():
        n, p = l_.split(':')
        n, p = n.strip(), p.strip()
        l.append(f'"{n}":"{p}"')
    return '{' + ','.join(l) + '}'

@app.route('/api/add', methods=['POST'])
@auth.login_required
def post():
    if not post_auth():
        return '{"error":"auth"}'
    post = request.form
    print(post, post['username'], post['password'])
    nm, pw = post['username'], post['password']
    l = f'{nm}:{pw}\n'
    with open('data.txt', 'a') as f:
        f.write(l)
        f.flush()
    return '["ok"]'

@app.route('/api/delete', methods=['POST'])
@auth.login_required
def delete():
    if not auth_in_url() or not post_auth():
        return '{"error":"auth"}'
    post = request.form
    nm = post['username']
    ls = open('data.txt', 'r').readlines()
    nls = []
    for l in ls:
        if not l.startswith(nm):
            nls.append(l)
    with open('data.txt', 'w') as f:
        f.write('\n'.join(nls))
        f.flush()
    return '["ok"]'

app.run('', 8888)
