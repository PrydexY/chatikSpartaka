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
admin_keys = ["aboba21062009"]
hash_keys = [str(hashlib.md5(keys[0].encode()).hexdigest())]
admin_hash_keys = [str(hashlib.md5(admin_keys[0].encode()).hexdigest())]
hash_keys += admin_hash_keys
print(hash_keys)

messages = messages_data_base()


@app.route('/')
def index(status=""):
    if not request.cookies.get("session") in hash_keys:
        return login(status)
    return render_template('index.html', old=messages.get_messages(), leng=len(messages.get_messages()))


@app.route('/', methods=["POST"])
def index_post():
    data = ast.literal_eval(request.data.decode("UTF-8"))
    req = render_template('login.html', old="<b>Неверный пасс-код!</b>")
    data["pass_code"].strip()
    print(data["pass_code"].strip(), keys)
    if str(hashlib.md5(data["pass_code"].encode()).hexdigest()) in hash_keys:
        req = redirect("")
        hashcode = hashlib.md5(data["pass_code"].encode()).hexdigest()
        req.set_cookie("username", data["username"])
        req.set_cookie("session", str(hashcode))
    return req


def login(status):
    if request.cookies.get("session") in hash_keys:
        index()
    return render_template('login.html', old=status)


@app.route("/admin")
def admin():
    print(request.cookies.get("session"), admin_hash_keys)
    if not request.cookies.get("session") in admin_hash_keys:
        return ""
    return render_template('admin.html', old="")


@socketio.on('message')
def handle_message(message):
    if not request.cookies.get("session") in hash_keys:
        return login("")
    message_text = message
    messages.add_message(request.cookies["username"], message_text)
    print(request.remote_addr, request.cookies["username"])
    if not request.remote_addr in black_list:
        emit('message', "<p><b>" + request.cookies["username"] + "</b> (" + str(
            datetime.datetime.now()) + ")</p><p>" + message_text + "</p>",
             broadcast=True)


@app.route("/files/<path:filename>")
def file(filename):
    if "/" in filename or "\\" in filename:
        return ""
    try:
        return send_file("files/" + filename)
    except:
        return ""


if __name__ == '__main__':
    socketio.run(app, port=80, host='0.0.0.0', allow_unsafe_werkzeug=True)
    messages.close()
