from flask import Flask, request, send_from_directory, redirect, render_template, url_for
from cryptography.fernet import Fernet

from sqlalchemy import create_engine, Column, String
from sqlalchemy.orm import declarative_base, sessionmaker
password = input("Type in cockroachdb password: ")
cockroachdb_engine = create_engine(f"cockroachdb://demo:{password}@127.0.0.1:26257/passwordstore?sslmode=require")
cockroachdb_session = sessionmaker(bind=cockroachdb_engine)
Base = declarative_base()

class UserData(Base):
    __tablename__ = "password_table"

    username = Column(String, primary_key=True)
    encryption_key = Column(String)
    encrypted_password = Column(String)

Base.metadata.create_all(cockroachdb_engine)

class Database:
    def __init__(self):
        self.session = cockroachdb_session()

    def store(self, entity: UserData) -> None:
        try:
            self.session.add(entity)
            self.session.commit()
        except:
            print("We tried to add something that already exists!")
            self.session.rollback()

    def fetch(self, name: str) -> UserData:
            return self.session.query(UserData).filter(UserData.username == name).one()

    def update(self, name: str, new_password: str):
        pass

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
    encrypted_password = str.encode(userdata.encrypted_password)
    encryption_key = str.encode(userdata.encryption_key)
    f = Fernet(encryption_key)
    print(encrypted_password)
    password = f.decrypt(encrypted_password).decode()


    # encryption_key = Fernet.generate_key()
    # f = Fernet(encryption_key)
    # password_encrypted = f.encrypt(str.encode(password))
    # userdata = UserData(password_encrypted, encryption_key)
    # database.store(user, userdata)
    # print(password_encrypted)

    url = url_for("hello_world", name=user, password=password)
    return redirect(url)

@app.route("/store", methods=["POST"])
def store():
    user = request.form["username"]
    password = request.form["password"]
    encryption_key = Fernet.generate_key()
    f = Fernet(encryption_key)
    encrypted_password = f.encrypt(str.encode(password))
    userdata = UserData(username=user,
                        encryption_key=encryption_key.decode(),
                        encrypted_password=encrypted_password.decode())
    database.store(userdata)
    return redirect(request.referrer)

@app.route("/showdb")
def showdb():
    print(database.entities)
    return "see console"


@app.route('/resources/<path>')
def send_resource(path):
    return send_from_directory('resources', path)
