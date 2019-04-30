from flask import Flask, flash, redirect, render_template, request, session
from flask_bootstrap import Bootstrap
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash

# Configure application
app = Flask(__name__)
Bootstrap(app)
@app.route("/")
def index():
    return render_template("index.html")
