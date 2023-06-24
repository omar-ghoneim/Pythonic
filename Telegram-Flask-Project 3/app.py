from flask import Flask, request, redirect, abort
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import hashlib
import base64
from keys import SECRET_CODE

app = Flask("__name__")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///shorturl.db"
db = SQLAlchemy(app)

base_url = "http://127.0.0.1:5000/"


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String(25), nullable=False)
    username = db.Column(db.String(25), nullable=False)
    chat_id = db.Column(db.String(50), nullable=False, unique=True)
    sub_status = db.Column(db.String(25), nullable=False, default="trial")
    links = db.relationship("Link", backref="author", lazy=True)

    def __repr__(self):
        return f"User('{self.fname}', '{self.username}', '{self.chat_id}', '{self.sub_status}')"


class Link(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original = db.Column(db.String(2048), nullable=False)
    short_code = db.Column(db.String(10), unique=True, nullable=False)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    def __repr__(self):
        return f"Links('{self.original}', '{self.short_code}', '{self.date_created}')"


def generate_code(username):
    no_of_link = Link.query.count()
    salt = str(no_of_link) + username
    code = hashlib.sha256((salt).encode()).digest()
    encoded_code = base64.urlsafe_b64encode(code[:6]).decode().rstrip("=")
    return encoded_code


def check_signature(timestamp, token):
    code = hashlib.sha256((timestamp + SECRET_CODE).encode()).digest()
    encoded_code = base64.urlsafe_b64encode(code).decode().rstrip("=")
    if encoded_code != token:
        return False
    return True


@app.route("/<string:code>")
def home(code):
    link = Link.query.filter_by(short_code=code).first_or_404()
    return redirect(link.original)


@app.route("/short")
def short():
    link = request.args.get("link")
    username = request.args.get("username")
    first_name = request.args.get("first_name")
    chat_id = request.args.get("chat_id")
    timestamp = request.headers.get("timestamp")
    token = request.headers.get("token")

    if not token or not timestamp:
        abort(403)
    is_authorized = check_signature(timestamp, token)
    if not is_authorized:
        abort(403)
    user = User.query.filter_by(chat_id=chat_id).first()

    if user:
        if user.sub_status == "trial" and len(user.links) >= 3:
            status = "failed"
            short_code = None
            result = {
                "chat_id": chat_id,
                "original_link": link,
                "short_code": short_code,
                "status": status,
            }
            return result
        else:
            status = "success"
            short_code = generate_code(username)
            short_link = base_url + short_code

    else:
        user = User(fname=first_name, username=username, chat_id=chat_id)
        db.session.add(user)
        db.session.commit()
        status = "success"
        short_code = generate_code(username)
        short_link = base_url + short_code

    new_link = Link(original=link, short_code=short_code, user_id=user.id)
    db.session.add(new_link)
    db.session.commit()

    result = {
        "chat_id": chat_id,
        "original_link": link,
        "short_code": short_code,
        "shortened_link": short_link,
        "status": status,
    }

    return result


@app.route("/check_user")
def check_user():
    chat_id = request.args.get("chat_id")
    timestamp = request.headers.get("timestamp")
    token = request.headers.get("token")
    if not token or not timestamp:
        abort(403)
    is_authorized = check_signature(timestamp, token)
    if not is_authorized:
        abort(403)
    user = User.query.filter_by(chat_id=chat_id).first()
    return str(user.sub_status)


@app.route("/sub")
def sub():
    user_id = request.args.get("user_id")
    first_name = request.args.get("first_name")
    timestamp = request.headers.get("timestamp")
    token = request.headers.get("token")
    if not token or not timestamp:
        abort(403)
    is_authorized = check_signature(timestamp, token)
    if not is_authorized:
        abort(403)
    user = User.query.filter_by(chat_id=user_id).first()
    user.sub_status = "subscribed"
    db.session.commit()
    return "OK"


if __name__ == "__main__":
    app.run(debug=True)
