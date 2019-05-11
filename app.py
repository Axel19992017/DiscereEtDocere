from flask import Flask, flash, redirect, render_template, request, session, make_response,json
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash
from flaskext.mysql import MySQL
from flask_mail import Message,Mail
# Configure application
app = Flask(__name__)
mail = Mail(app)
"""
    FALTA: AGREGAR ADMINISTRACIÓN
    MOSTRAR IMAGENES
    AGREGAR INICIO
    AGREGAR FORO
"""
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
alias = ''
error = ''
foroS = tuple()
respuestas = list()
# Funciones usadas con propositos de utilidad
def getCorreo(alias):
    cursor.execute(f"select email from Usuario where alias = BINARY '{alias}' ;")
    res = cursor.fetchone()
    return res[0]  
def getidUsuario(alias):
    cursor.execute(f"select idUsuario from Usuario where alias = BINARY '{alias}' ;")
    res = cursor.fetchone()
    return res[0]
def getTemas(unidadSelec):
    if unidadSelec is None:
        cursor.execute('select T.idUnidad, T.idTema , T.nombre, T.descripcion from Tema T;')
    else:
        cursor.callproc('getTemas',(unidadSelec))
    return cursor.fetchall()
# Obtener unidades agregadas a la base de datos
def getUnidades():
    cursor.execute('select * from Unidad')
    return cursor.fetchall()
#Agregar usuario a la base de datos
def addUsuarioDB(nombres,apellidos,email,gradoAcad,alias,pase,foto):
    cursor.callproc('addUsuario',(nombres,apellidos,gradoAcad,email,alias,pase,foto,'basic'))
    cursor.connection.commit()
# Si existe un Usuario con ese alias (el alias es único)
def siExisteUsuario(alias, pase):
    if pase is None:
        cursor.execute(f"select count(*) as Vacio from Usuario where alias = BINARY '{alias}';")
        vacio = cursor.fetchone()
        return vacio[0]
    else:
        cursor.execute(f"select count(*) as Vacio from Usuario where alias = BINARY '{alias}' and pase = BINARY '{pase}';")
        vacio = cursor.fetchone()
        return vacio[0]
#Averiguar si un correo está registrado o ligado a un Usuario
def siCorreoRegistrado(correo):
    cursor.execute(f"select count(*) as Vacio from Usuario where email = BINARY '{correo}'")
    vacio = cursor.fetchone()
    if vacio[0] == 1:
        return True
    else:
        return False
#Obtener un rol
def getRol(alias):
    cursor.execute(f"select rol from Usuario where alias = BINARY '{alias}'")
    rol = cursor.fetchone()
    return rol[0]
@app.route("/")
def index():
    cursor.execute("select CONCAT(nombre,' ',apellido) as Nombre,alias,pase from Usuario;")
    print(cursor.rownumber)
    rows = cursor.fetchall()
    return render_template("index.html",rows = rows,rol = rol,alias=alias)

@app.route("/login")
def login():
    print(f'El rol es: ' + rol)
    return render_template("login.html",error = "")

@app.route("/salir")
def salir():
    global rol
    global alias
    rol= ""
    alias = ""
    return render_template("index.html",rol= rol, alias = alias)

@app.route("/contacto")
def contacto():
    return render_template("contacto.html", rol = rol, alias = alias)

@app.route("/enviarMail", methods=['GET'])
def enviarMail():
    print("Método aún en proceso")
    '''global alias
    contenido = request.args.get("mensaje")
    correo = getCorreo(alias)
    msg  =  Message(contenido,sender = correo ,recipients = ["agarciadarce@gmail.com"])
    mail.send(msg)'''
    return render_template("index.html",rol= rol, alias = alias, mensaje = "Soporte ha recibido tu mensaje")

@app.route("/inicioSesion", methods=['POST'])
def inicioSesion():
    global alias
    alias = request.form['usuario']
    pase = request.form['pase']
    if not alias or not pase:
        error = 'Datos ingresados incorrectamente'
        return render_template("login.html", error = error)
    elif siExisteUsuario(alias,pase) == 0:
        error = 'Usuario o contraseña incorrectos'
        return render_template("login.html", error = error)
    else:
        global rol
        rol = getRol(alias)
        return render_template("index.html",rol= rol, alias = alias)
@app.route("/addUsuario")
def addUsuario():
    return render_template("registrarUsuario.html")

@app.route("/addingUsuario", methods=['POST'])
def addingUsuario():
    nombres = request.form['nombres']
    apellidos = request.form['apellidos']
    correo = request.form['correo']
    gradoAcad = request.form['gradoAcad']
    alias = request.form['alias']
    pase = request.form['pass']
    paseConf = request.form['passReenv']
    errores = list()

    if siExisteUsuario(alias,None) == 1:
        errores.append('El usuario ya está en uso! :c')
    if pase != paseConf:
        errores.append("Las contraseñas no son iguales >:D")
    if siCorreoRegistrado(correo):
        errores.append('El correo ya pertenece a un usuario >:c')
    if not errores:
        addUsuarioDB(nombres,apellidos,correo,gradoAcad,alias,pase,None)
        return render_template("login.html", mensaje = "Usuario Registrado, ya puede ingresar")
    else:
        return render_template("registrarUsuario.html", errores = errores)
@app.route("/foro")
def foro():
    unidades = getUnidades()
    temas = getTemas(None)
    return render_template('foro.html',unidades =unidades, temas =temas,rol =rol, alias = alias )

@app.route("/getForos", methods=['GET'])
def getForos():
    idTema = request.args.get('idTema')
    cursor.execute(f"select F.idForo, T.nombre as TemaUnidad, U.alias, F.nombre as TemaForo, F.descripcion, F.archivo, F.horaCreacion from Foro F inner join Tema T on T.idTema=F.idTema inner join Usuario U on U.idUsuario = F.idUsuario where F.idTema = {idTema};")
    ResultSet = cursor.fetchall()
    forosList = []
    for foro in ResultSet:
        foroDict = {
            'idForo': foro[0],
            'TemaUnidad': foro[1],
            'alias': foro[2],
            'TemaForo': foro[3],
            'descripcion': foro[4],
            'horaCreacion': foro[6]
        }
        forosList.append(foroDict)
    return json.dumps(forosList, sort_keys=True, indent=4)
@app.route('/responderForo', methods=['GET'])
def responderForos():
    global respuestas
    global foroS
    idForo = request.args.get('idForo')
    cursor.execute(f"select RF.idRespuestaForo,U.alias , RF.contenido, RF.archivo, RF.horaResp from RespuestaForo RF inner join Usuario U on U.idUsuario = RF.idUsuario where idForo={idForo} order by horaResp asc;")
    respuestas = cursor.fetchall()
    cursor.execute(f"select F.idForo, T.nombre as TemaUnidad, U.alias, F.nombre as TemaForo, F.descripcion, F.archivo, F.horaCreacion from Foro F inner join Tema T on T.idTema=F.idTema inner join Usuario U on U.idUsuario = F.idUsuario where F.idForo = {idForo};")
    foroS = cursor.fetchone()
    return render_template('respuestas.html',alias = alias,rol =rol,foro = foroS, respuestas = respuestas)

@app.route('/addRespuesta', methods=['GET'])
def addRespuesta():
    global respuestas
    global foroS
    idForo = request.args.get('idForo')
    contenido = request.args.get('contenido')
    alias = request.args.get('alias')
    idUsuario = getidUsuario(alias)
    cursor.callproc('addRespuesta',(idForo,idUsuario,contenido,None))
    cursor.connection.commit()
    print('Respuesta agregada!!')
    cursor.execute(f"select RF.idRespuestaForo,U.alias , RF.contenido, RF.archivo, RF.horaResp from RespuestaForo RF inner join Usuario U on U.idUsuario = RF.idUsuario where idForo={idForo} order by horaResp asc;")
    respuestas = cursor.fetchall()
    return render_template('respAdd.html',respuestas = respuestas)
@app.route('/addForo', methods=['GET'])
def addForo():
    idTema = request.args.get('idTema')
    alias = request.args.get('alias')
    idUsuario = getidUsuario(alias)
    nombre = request.args.get('nombre')
    contenido = request.args.get('contenido')
    cursor.callproc('addForo',(idTema,idUsuario,nombre,contenido,None))
    cursor.connection.commit()
    return '202'
@app.route('/perfil')
def perfil():
    global alias
    cursor.execute(f"select CONCAT(nombre,' ',apellido) AS Nombre, gradoAcademico, email, alias from Usuario where alias = BINARY '{alias}';")
    res = cursor.fetchone()
    return render_template('perfil.html', rol = rol, alias = alias, datosUsuario = res)


if __name__ == '__main__':
    app.run(debug=True, port=5500)
