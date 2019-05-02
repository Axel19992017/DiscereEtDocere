from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash
from flaskext.mysql import MySQL
# Configure application
app = Flask(__name__)
mysql = MySQL()
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_PORT'] = '3306'
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'Axel0611.'
app.config['MYSQL_DATABASE_DB'] = 'DED'
mysql.init_app(app)
@app.route("/")
def index():
    
    return render_template("index.html")

if __name__ == '__main__':
    app.run(debug=True)