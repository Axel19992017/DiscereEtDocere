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
app.config['MYSQL_DATABASE_PORT'] = 3306
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'Axel0611.'
app.config['MYSQL_DATABASE_DB'] = 'DED'

mysql.init_app(app)
con = mysql.connect()
cursor = con.cursor()
rol = ''
error = ''
# Funciones usadas con propositos de utilidad

# Si existe un Usuario con ese alias (el alias es único)
def siExisteUsuario(alias, pase):
    cursor.execute(f"select count(*) as Vacio from Usuario where alias = '{alias}' and pase = '{pase}';")
    vacio = cursor.fetchone()
    return vacio[0]
def getRol(alias):
    cursor.execute(f"select rol from Usuario where alias = '{alias}'")
    rol = cursor.fetchone()
    return rol[0]
@app.route("/")
def index():
    cursor.execute("select CONCAT(nombre,' ',apellido) as Nombre,alias,pase from Usuario;")
    print(cursor.rownumber)
    rows = cursor.fetchall()
    return render_template("index.html",rows = rows,rol = rol)

@app.route("/login")
def login():
    print(f'El rol es: ' + rol)
    return render_template("login.html",error = "")

@app.route("/inicioSesion", methods=['POST'])
def inicioSesion():
    usuario = request.form['usuario']
    pase = request.form['pase']
    if not usuario or not pase:
        error = 'Datos ingresados incorrectamente'
        return render_template("login.html", error = error)
    elif siExisteUsuario(usuario,pase) == 0:
        error = 'Usuario o contraseña incorrectos'
        return render_template("login.html", error = error)
    else:
        rol = getRol(usuario)
        return render_template("index.html",rol= rol)

@app.route("/addUsuario")
def addUsuario():
    return render_template("registrarUsuario.html")
if __name__ == '__main__':
    app.run(debug=True)

