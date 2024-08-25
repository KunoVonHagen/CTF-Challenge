import random
import sqlite3
import hashlib
import time
import server as db_server
import os
import random
import string

def generate_random_alphanumeric(n):
    alphanumeric_characters = string.ascii_letters + string.digits
    random_characters = random.choices(alphanumeric_characters, k=n)
    return ''.join(random_characters)


# SQLite database file
DB_FILE = 'database.db'
conn = sqlite3.connect(DB_FILE, check_same_thread=False)

def init_db():
    monitoring_session_secret = "3pahdksbnfpdz6v1"

    hashed_admin_password = hashlib.md5(os.getenv("BACKEND_ADMIN_PASSWORD").encode()).hexdigest()
    hashed_monitoring_password = hashlib.md5(generate_random_alphanumeric(16).encode()).hexdigest()
    monitoring_session = hashlib.md5(monitoring_session_secret.encode()).hexdigest()
    now = int(time.time())

    cursor = conn.cursor()
    cursor.execute(f"INSERT INTO users (username, password, has_privileges) VALUES ('admin', '{hashed_admin_password}', 1)")
    cursor.execute(f"INSERT INTO users (username, password, has_privileges) VALUES ('monitoring', '{hashed_monitoring_password}', 1)")
    cursor.execute(f"INSERT INTO sessions (session, username, created_at) VALUES ('{monitoring_session}', 'monitoring', {now})")
    conn.commit()
    cursor.close()


def session_cookie():
    return hashlib.md5((str(random.randint(10000,20000)) + str(time.time()) + "S3cr3t").encode()).hexdigest()


def get_cats():
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM cats")
    cats = cursor.fetchall()

    res = []
    for _, name, picture, filetype in cats:
        res.append({'name': name, 'picture': picture, 'filetype': filetype})

    cursor.close()

    return {"cats": res}


def insert_user_if_not_exists(username, password):
    hashed_password = hashlib.md5(password.encode()).hexdigest()
    success = False
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM users WHERE username='{username}'")
    user = cursor.fetchone()

    if user is None:
        cursor.execute(f"INSERT INTO users (username, password, has_privileges) VALUES ('{username}', '{hashed_password}', 0)")
        conn.commit()
        success = True

    return {'success': success}


def is_valid_session(session):
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM sessions WHERE session='{session}'")
    session = cursor.fetchone()

    return {'success': session is not None}


def is_priviliged_session(session):
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM sessions, users WHERE sessions.username=users.username AND sessions.session='{session}' AND users.has_privileges=1")
    session = cursor.fetchone()
    cursor.close()

    return {'success': session is not None}


def logout_user(session):
    cursor = conn.cursor()
    cursor.execute(f"DELETE FROM sessions WHERE session='{session}'")
    conn.commit()
    cursor.close()

    return {'success': True}


def get_user_session(username, password):
    hashed_password = hashlib.md5(password.encode()).hexdigest()
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM users WHERE username='{username}' AND password='{hashed_password}'")
    user = cursor.fetchone()
    cursor.close()

    if user is not None:
        session = session_cookie()
        now = int(time.time())

        cursor = conn.cursor()
        cursor.execute(f"INSERT INTO sessions (session, username, created_at) VALUES ('{session}', '{user[0]}', {now})")
        conn.commit()
        cursor.close()
        return {'success': True, 'session': session}

    return {'success': False}


def get_temp_session():
    session = session_cookie()
    now = int(time.time())

    cursor = conn.cursor()
    cursor.execute(f"INSERT INTO sessions (session, username, created_at) VALUES ('{session}', 'tmp', {now})")
    conn.commit()
    cursor.close()

    return {'session': session}


def is_user_session(session):
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM sessions WHERE session='{session}' AND username!='tmp'")
    session = cursor.fetchone()
    cursor.close()

    return {'success': session is not None}


def add_comment(author, comment):
    cursor = conn.cursor()
    cursor.execute(f"INSERT INTO comments (author, content, time_written) VALUES ('{author}', '{comment}', {time.time()})")
    conn.commit()
    cursor.close()

    return {'success': True}


def get_session_username(session):
    cursor = conn.cursor()
    cursor.execute(f"SELECT username FROM sessions WHERE session='{session}'")
    username = cursor.fetchone()
    cursor.close()

    if username is not None and username != 'tmp':
        return {'success': True, 'username': username[0]}

    return {'success': False}

def get_comments():
    cursor = conn.cursor()
    comments = cursor.execute("SELECT * FROM comments").fetchall()
    cursor.close()

    res = []
    for content, _, author, time_written in comments:
        formatted_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time_written))
        res.append({'author': author, 'content': content, 'time_written': formatted_time})

    return {'comments': res}


def add_cat(name, picture, filetype):
    cursor = conn.cursor()
    cursor.execute(f"INSERT INTO cats (name, picture, filetype) VALUES ('{name}', '{picture}', '{filetype}')")
    conn.commit()
    cursor.close()

    return {'success': True}


actions = {"signup-user": insert_user_if_not_exists,
           "check-privileged-session": is_priviliged_session,
           "logout-user": logout_user,
           "get-user-session": get_user_session,
           "get-temp-session": get_temp_session,
           "add-comment": add_comment,
           "get-username-from-session": get_session_username,
           "get-comments": get_comments,
           "get-cats": get_cats,
           "add-cat": add_cat}

key = b'iT\xe1\xb47\xa3\xad\xfe$\x96\x82:H\x0b\x9d\xc3'
iv = b"\xab\xd3\x11'\xa1\x83\xad.)\x1e\xf8\x13\xfc]\xe5\x1d"

init_db()

server = db_server.DatabaseServer('0.0.0.0', 3306, actions, key, iv)
server.run()

