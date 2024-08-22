import json
from flask import Flask, request, render_template_string, redirect, url_for, make_response
import subprocess
import os
import datetime
import requests
from base64 import b64encode, b64decode
from werkzeug.middleware.profiler import ProfilerMiddleware
import client as db_client

app = Flask(__name__)

#app.config['PROFILE'] = True
#app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[30])

database_server_addr = "backend.ctf-challenge.edu"
database_server_port = 3306
NUM_DB_CLIENTS = 5

key = b'iT\xe1\xb47\xa3\xad\xfe$\x96\x82:H\x0b\x9d\xc3'
iv = b"\xab\xd3\x11'\xa1\x83\xad.)\x1e\xf8\x13\xfc]\xe5\x1d"
client = db_client.DatabaseClient(database_server_addr, database_server_port, key, iv)

db_clients = [[db_client.DatabaseClient(database_server_addr, database_server_port, key, iv), True] for i in range(NUM_DB_CLIENTS)]

def db_request(action, **kwargs):
    global db_clients
    client = None
    index = None
    
    while client is None:
        for i in range(len(db_clients)):
            if db_clients[i][1]:
                db_clients[i][1] = False
                client = db_clients[i][0]
                index = i
                break
    
    result = client.request(action, **kwargs)
    db_clients[index][1] = True
    
    return result
    

status = {
    "/": {"title": "Index", "code": "200", "description": "OK"},
    "/admin": {"title": "Admin", "code": "200", "description": "OK"},
    "/login": {"title": "Admin Login", "code": "200", "description": "OK"},
    "/monitoring-test": {"title": "Monitoring Test (switches between 200, 403, 404)", "code": "200", "description": "OK"},
    "/status": {"title": "Status", "code": "200", "description": "OK"},
}

last_update = datetime.datetime.now().strftime("%d.%m.%Y - %H:%M:%S")

pages = [
    {"title": "Index", "url": "/"},
    {"title": "Update Status", "url": "/update-status"},
    {"title": "Admin", "url": "/admin"},
    {"title": "Admin Login", "url": "/admin-login"},
    {"title": "Add Page", "url": "/admin/add-page"}
]

dynamic_pages = []

monitoring_values = [200, 403, 404]
actual_monitor_test = 0

header = open("templates/header.html").read()


def sanitize_to_b64_chars(input):
    allowed_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789+/="
    return "".join([c for c in input if c in allowed_chars])


def valid_username(username):
    allowed_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    return all([c in allowed_chars for c in username])


def get_temp_session():
    res = db_request('get-temp-session')
    session = res['session']
    return session


def get_user_session(username, password):
    res = db_request('get-user-session', username=username, password=password)
    session = res['session'] if res['success'] else None
    return session


def signup_user(username, password):
    res = db_request('signup-user', username=username, password=password)
    return res['success'], res['message']


def add_comment(session, comment):
    session = sanitize_to_b64_chars(session)
    b64_comment = b64encode(comment.encode()).decode()
    res = db_request('add-comment', session=session, comment=b64_comment)
    return res['success']


def get_comments():
    res = db_request('get-comments')
    decoded_comments = [b64decode(comment).decode() for comment in res['comments']]
    return decoded_comments


def check_privileged_session(session):
    session = sanitize_to_b64_chars(session)
    res = db_request('check-privileged-session', session=session)
    privilege = res['success']
    return privilege


def get_username_from_session(session):
    session = sanitize_to_b64_chars(session)
    res = db_request('get-username-from-session', session=session)
    username = res['username'] if res['success'] else None
    return username if username != 'tmp' else None


def logout_user(session):
    session = sanitize_to_b64_chars(session)
    res = db_request('logout-user', session=session)
    return res['success']

def redirect_with_session(location, new_session=False):
    response = redirect(location)
    if "session" not in request.cookies or new_session:
        response.set_cookie("session", get_temp_session())
    return response


def render_template_with_session(html, **kwargs):
    html = header + html

    if "session" not in request.cookies:
        response = make_response(render_template_string(html, **kwargs))
        response.set_cookie("session", get_temp_session())
        return response

    username = get_username_from_session(request.cookies.get("session"))
    return render_template_string(html, username=username, **kwargs)


def render_template_file_with_session(file, **kwargs):
    html = open("templates/" + file).read()
    return render_template_with_session(html, **kwargs)

@app.route('/')
def index():
    comments = get_comments()
    if comments == ['']:
        comments = []
    return render_template_file_with_session("index.html", status=status, comments=comments)


@app.route('/submit', methods=['POST'])
def submit():
    comment = request.form['comment']
    session = request.cookies.get('session')

    add_comment(session, comment)
    return redirect_with_session(url_for('index')), 303


@app.route('/update-status', methods=['GET', 'POST'])
def update_status():
    global status
    global last_update
    session = request.cookies.get('session')
	
    if not session or not check_privileged_session(session):
        return render_template_file_with_session("403_not_privileged.html"), 403

    if request.method == 'POST':
        status_update = json.loads(request.data)['status_update']
        status[status_update['url']] = {"title": status_update['title'], "code": status_update['code'], "description": status_update['description']}
        last_update = datetime.datetime.now().strftime("%d.%m.%Y - %H:%M:%S")
        return redirect_with_session(url_for('index')), 303

    return render_template_file_with_session('update_status.html'), 200


@app.route('/status')
def get_status():
    global last_update
    return render_template_file_with_session('status.html', status=status, last_update=last_update), 200


@app.route('/admin/pages', methods=['GET'])
def admin_pages():
    session = request.cookies.get('session')
    if not session or not check_privileged_session(session):
        return render_template_file_with_session("403_not_privileged.html"), 403
    return render_template_file_with_session('admin_pages.html', pages=pages + dynamic_pages), 200


@app.route('/admin/add-page', methods=['GET', 'POST'])
def add_page():
    session = request.cookies.get('session')
    if not session or not check_privileged_session(session):
        return render_template_file_with_session("403_not_privileged.html"), 403

    if request.method == 'POST':
        title = request.form['title']
        url = request.form['url']
        content = request.form['content']
        if url in [page['url'] for page in pages + dynamic_pages]:
            return render_template_file_with_session('400_url_in_use.html'), 400
        if not url.startswith('/') or any(c in url for c in ['.', ' ']):
            return render_template_file_with_session('400_invalid_url.html'), 400
        dynamic_pages.append({"title": title, "url": url, "content": content})
        return redirect_with_session(url_for('admin_pages')), 303

    return render_template_file_with_session('add_page.html'), 200


@app.route('/<page>')
def dynamic_page(page):
    for p in dynamic_pages:
        if p['url'] == f'/{page}':
            with open('temp', 'w') as file:
                file.write(p['content'])
            proc = subprocess.Popen(["php", "temp"], stdout=subprocess.PIPE)
            template = ''
            while buffer := proc.stdout.read().decode("latin-1"):
                template += buffer
            proc.wait()
            template += proc.stdout.read().decode("latin-1")
            os.remove('temp')
            return render_template_with_session(template), 200
    return render_template_file_with_session('404.html'), 404


@app.route('/monitoring-test')
def monitoring_test():
    global actual_monitor_test
    file = f'{monitoring_values[actual_monitor_test]}_monitoring_test.html'
    actual_monitor_test = (actual_monitor_test + 1) % len(monitoring_values)
    return render_template_file_with_session(file), monitoring_values[actual_monitor_test]


@app.route('/admin', methods=['GET'])
def admin():
    session = request.cookies.get('session')
    if not session or not check_privileged_session(session):
        return render_template_file_with_session("403_not_privileged.html"), 403
    return render_template_file_with_session('admin.html'), 200


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        session = get_user_session(username, password)
        if session:
            response = redirect(url_for('index'))
            response.set_cookie('session', session)
            return response, 303
        return render_template_file_with_session('403_invalid_credentials.html'), 403
    return render_template_file_with_session('login.html'), 200


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session = request.cookies.get('session')
    if session:
        logout_user(session)

    return redirect_with_session(url_for('index'), True), 303


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
