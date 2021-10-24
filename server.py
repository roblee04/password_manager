from flask import Flask, request, send_from_directory, redirect, render_template, url_for
from cryptography.fernet import Fernet

class UserData:
    def __init__(self, encrypted_password, encryption_key):
        self.encrypted_password = encrypted_password
        self.encryption_key = encryption_key

class Database:
    def __init__(self):
        self.entities = {}

    def store(self, key: str, value: UserData) -> None:
        self.entities[key] = value

    def fetch(self, key: str):
        if key in self.entities:
            return self.entities[key]
        return None

app = Flask(__name__, template_folder="resources")
database = Database()

@app.route("/")
@app.route("/<name>/<password>")
def hello_world(name=None, password=None):
    # return send_from_directory('resources', 'hello.html')
    return render_template("hello.html", name=name, password=password)

@app.route("/fetch", methods=["POST"])
def fetch():
    user = request.form["username"]
    userdata = database.fetch(user)
    encrypted_password = userdata.encrypted_password
    encryption_key = userdata.encryption_key
    f = Fernet(encryption_key)
    password = f.decrypt(encrypted_password).decode()
    url = url_for("hello_world", name=user, password=password)
    return redirect(url)
    # return redirect(request.referrer)

@app.route("/store", methods=["POST"])
def store():
    user = request.form["username"]
    password = request.form["password"]
    encryption_key = Fernet.generate_key()
    f = Fernet(encryption_key)
    encrypted_password = f.encrypt(str.encode(password))
    userdata = UserData(encrypted_password, encryption_key)
    database.store(user, userdata)
    return redirect(request.referrer)

@app.route("/showdb")
def showdb():
    print(database.entities)
    return "see console"


@app.route('/resources/<path>')
def send_resource(path):
    return send_from_directory('resources', path)
