from flask import Flask, render_template, send_file, redirect, url_for
from flask_socketio import SocketIO, emit
import datetime
from flask import request
from db_manager import *
import ast
import hashlib

app = Flask(__name__)
app.config['SECRET_KEY'] = 'chatik'
socketio = SocketIO(app)
black_list = []
keys = ["aboba"]
hash_keys = [str(hashlib.md5(keys[0].encode()).hexdigest())]

messages = messages_data_base()


@app.route('/')
def index():
    if not request.cookies.get("session") in hash_keys:
        return login()
    return render_template('index.html', old=messages.get_messages(), leng=len(messages.get_messages()))


@app.route('/', methods=["POST"])
def index_post():
    data = ast.literal_eval(request.data.decode("UTF-8"))
    req = render_template('login.html', old="Неверный пасс-код!")
    print(data["pass_code"], keys)
    if data["pass_code"] in keys:
        req = redirect("")
        hashcode = hashlib.md5(data["pass_code"].encode()).hexdigest()
        req.set_cookie("username", data["username"])
        req.set_cookie("session", str(hashcode))
    return req


def login():
    if request.cookies.get("session") in hash_keys:
        index()
    return render_template('login.html', old="")


@socketio.on('message')
def handle_message(message):
    if not request.cookies.get("session") in hash_keys:
        return login()
    message_text = message.split(", ")[1]
    name = message.split(", ")[0]
    messages.add_message(name, message_text)
    print(request.remote_addr, name)
    if not request.remote_addr in black_list:
        emit('message', "<b>" + name + "</b> (" + str(datetime.datetime.now().hour) + ":" + str(
            datetime.datetime.now().minute) + ":" + str(
            datetime.datetime.now().second) + ")<br><br>" + message_text,
             broadcast=True)


@app.route("/files/<path:filename>")
def file(filename):
    if "/" in filename or "\\" in filename:
        return ""
    return send_file("files/" + filename)


if __name__ == '__main__':
    socketio.run(app, port=80, host='0.0.0.0', allow_unsafe_werkzeug=True)
    messages.close()
