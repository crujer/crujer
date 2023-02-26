from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_mysqldb import MySQL
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import check_password_hash, generate_password_hash
from config import config
import database as db
import os, mysql.connector
from models.ModelUser import ModelUser
from models.entites.User import User
from werkzeug.utils import secure_filename                                          #para q no se suban (upload) archivos con extenciones potencialmente daninas
from flask_httpauth import HTTPBasicAuth # PARA ROLES

#--- Carga Imagenes ---
UPLOAD_FOLDER = os.path.abspath("./uploads/")                                       #Ruta donde se van a guardar los archivos cargados
ALLOWED_EXTENSIONS = set(["png", "jpg", "jpge"])                                    #Extensiones permitidas para cargar archivos

def allowed_file(filename):                                                         #creamos una funcion q nos permita validar la extension de nuestros archivos y pasamos como parametro el nombre de nuestro archivo (filename)
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS #devuelve si detencta un punto (".") en nuestro archivo (filename) y (and) el archivo lo va a dividir en el punto una vez (filename rsplit(".", 1)) y vamos a usar la parte q dividio despues del punto indicando q vamos a usar la segunda parte de la variable asignada [1].lower() in ALLOWED_EXTENSIONS

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
auth = HTTPBasicAuth() # PARA ROLES

db=MySQL(app)
login_manager_app=LoginManager(app)                                                 #Creo variable y le paso la app

@login_manager_app.user_loader                                                      #y creamos un metodo de cargador de usuario 
def load_user(id):                                                                  #creo funcion pasandole id
    return ModelUser.get_by_id(db, id)                                              #devuelve todos los datos del usuario pasandole la variable de coneccion e identificador

@app.route('/')
def index():
    return render_template('index.html')

# INICIO Ruta LOGIN / LOGOUT / REGISTRO:
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method=='POST' :
        user = User(0,request.form['username'],request.form['password'])
        logged_user=ModelUser.login(db,user)
        if logged_user != None:
            if logged_user.password:
                login_user(logged_user)                                             #para q almacene usuario logeado
                return redirect(url_for('home'))
            else:
                flash("Password Invalido...")
                return render_template('auth/login.html')
        else:
            flash("Usuario No Encontrado...")
            return render_template('auth/login.html')
    else:
        return render_template('auth/login.html')

@app.route('/logout')
def logout():
   logout_user()                                                                    #llamamos la funcion q habiamos importado
   return redirect(url_for('login'))                                                #vuelve a login

@app.route('/registro')                                                            
def registro():                                      
    return render_template('registro.html')

@app.route('/registro', methods=['POST'])
def addregistro():
    db = mysql.connector.connect(
    host='localhost',
    user='crujer',
    password='00arg1428',
    database='test'
    )

    username = request.form['username']
    passw = request.form['password']
    confirmacion = request.form['confirmacion']
    fullname = request.form['fullname']
    password = generate_password_hash(passw)
    mail = request.form['mail']

    if passw == confirmacion:
        if username and password and fullname and mail:
            cursor = db.cursor()
            sql = "INSERT INTO user (username, password, fullname, mail) VALUES (%s, %s, %s, %s)"
            data = (username, password, fullname, mail)
            cursor.execute(sql, data)
            db.commit()
            flash("Registrado Exitosamente !!")
    else:
        flash("Password no coincide...")
    return redirect(url_for('registro'))

# INICIO ROLES --> https://flask-httpauth.readthedocs.io/en/latest/

@auth.get_user_roles
def get_user_roles(user):
    return user.get_roles()

@app.route('/admin')
@auth.login_required(role='admin')
def admins_only():
    return "Hello {}, you are an admin!".format(auth.current_user())

# INICIO Ruta HOME
@app.route('/home')
@login_required 
def home():
   return render_template('home.html')

# INICIO Ruta USUARIOS en DB
@app.route('/usuarios') 
@login_required 
def usuarios():                                           
    db = mysql.connector.connect(
    host='localhost',
    user='crujer',
    password='00arg1428',
    database='test'
    )

    cursor = db.cursor()
    cursor.execute("SELECT * FROM users")
    myresult = cursor.fetchall()
    #Convertir los datos a diccionario
    insertObject = []
    columnNames = [column[0] for column in cursor.description]
    for record in myresult:
        insertObject.append(dict(zip(columnNames, record)))
    cursor.close()
    return render_template('usuarios.html', data=insertObject)

@app.route('/user', methods=['POST'])
def addUser():
    db = mysql.connector.connect(
    host='localhost',
    user='crujer',
    password='00arg1428',
    database='test'
    )

    apellido = request.form['apellido']
    nombre = request.form['nombre']
    id_tw = request.form['id_tw']
    fecha = request.form['fecha']
    hs = request.form['hs']

    if apellido and nombre and id_tw and fecha and hs:
        cursor = db.cursor()
        sql = "INSERT INTO users (apellido, nombre, id_tw, fecha, hs) VALUES (%s, %s, %s, %s, %s)"
        data = (apellido, nombre, id_tw, fecha, hs)
        cursor.execute(sql, data)
        db.commit()
    return redirect(url_for('usuarios'))

@app.route('/delete/<string:id>')
def delete(id):
    db = mysql.connector.connect(
    host='localhost',
    user='crujer',
    password='00arg1428',
    database='test'
    )

    cursor = db.cursor()
    sql = "DELETE FROM users WHERE id=%s"
    data = (id,)
    cursor.execute(sql, data)
    db.commit()
    return redirect(url_for('usuarios'))

@app.route('/edit/<string:id>', methods=['POST'])
def edit(id):
    db = mysql.connector.connect(
    host='localhost',
    user='crujer',
    password='00arg1428',
    database='test'
    )

    apellido = request.form['apellido']
    nombre = request.form['nombre']
    id_tw = request.form['id_tw']
    fecha = request.form['fecha']
    hs = request.form['hs']

    if apellido and nombre and id_tw and fecha and hs:
        cursor = db.cursor()
        sql = "UPDATE users SET apellido = %s, nombre = %s, id_tw = %s, fecha = %s, hs = %s WHERE id = %s"
        data = (apellido, nombre, id_tw, fecha, hs, id)
        cursor.execute(sql, data)
        db.commit()
    return redirect(url_for('usuarios'))

@app.route('/ordenar', methods=['POST'])
def ordenar_desc():
    db = mysql.connector.connect(
    host='localhost',
    user='crujer',
    password='00arg1428',
    database='test'
    )
    
    cursor = db.cursor()
    categoria = request.form['categoria_ordenar']
    estilo = request.form['estilo']

    #"SELECT * FROM users ORDER BY id DESC"
    cursor.execute("SELECT * FROM users ORDER BY {} {}".format(categoria, estilo))
    myresult = cursor.fetchall()
    #Convertir los datos a diccionario
    insertObject = []
    columnNames = [column[0] for column in cursor.description]
    for record in myresult:
        insertObject.append(dict(zip(columnNames, record)))
    cursor.close()
    return render_template('usuarios.html', data=insertObject)

@app.route('/buscador_usuario', methods=['POST']) # /<string:id>', methods=['POST'])
def buscar_usuario():                                           
    db = mysql.connector.connect(
    host='localhost',
    user='crujer',
    password='00arg1428',
    database='test'
    )

    cursor = db.cursor()
    categoria = request.form['categoria']
    buscador = request.form['buscador']
    #cursor.execute("SELECT * FROM users WHERE apellido = '{}'".format(buscador))
    cursor.execute("SELECT * FROM users WHERE {} = '{}'".format(categoria,buscador))
    myresult = cursor.fetchall()
    #Convertir los datos a diccionario
    insertObject = []
    columnNames = [column[0] for column in cursor.description]
    for record in myresult:
        insertObject.append(dict(zip(columnNames, record)))
    cursor.close()
    return render_template('usuarios.html', data=insertObject)

# INICIO Ruta LISTA CLIENTES en DB
@app.route('/lista_cliente') #la asociamos
@login_required
def lista_cliente():                                           
    db = mysql.connector.connect(
    host='localhost',
    user='crujer',
    password='00arg1428',
    database='test'
    )

    cursor = db.cursor()
    cursor.execute("SELECT * FROM lista_cliente")
    myresult = cursor.fetchall()
    #Convertir los datos a diccionario
    insertObject = []
    columnNames = [column[0] for column in cursor.description]
    for record in myresult:
        insertObject.append(dict(zip(columnNames, record)))
    cursor.close()
    return render_template('lista_cliente.html', data=insertObject)

@app.route('/lista_cliente', methods=['POST'])
def addCliente():
    db = mysql.connector.connect(
    host='localhost',
    user='crujer',
    password='00arg1428',
    database='test'
    )

    apellido = request.form['apellido']
    nombre = request.form['nombre']
    tel = request.form['tel']
    email = request.form['email']
    idtw = request.form['idtw']
    comentario = request.form['comentario']

    if apellido and nombre and tel and email and idtw and comentario:
        cursor = db.cursor()
        sql = "INSERT INTO lista_cliente (apellido, nombre, tel, email, idtw, comentario) VALUES (%s, %s, %s, %s, %s, %s)"
        data = (apellido, nombre, tel, email, idtw, comentario)
        cursor.execute(sql, data)
        db.commit()
    return redirect(url_for('lista_cliente'))

@app.route('/delete_lista_cliente/<string:id>')
def delete_lista_cliente(id):
    db = mysql.connector.connect(
    host='localhost',
    user='crujer',
    password='00arg1428',
    database='test'
    )

    cursor = db.cursor()
    sql = "DELETE FROM lista_cliente WHERE id=%s"
    data = (id,)
    cursor.execute(sql, data)
    db.commit()
    return redirect(url_for('lista_cliente'))

@app.route('/edit_lista_cliente/<string:id>', methods=['POST'])
def edit_lista_cliente(id):
    db = mysql.connector.connect(
    host='localhost',
    user='crujer',
    password='00arg1428',
    database='test'
    )

    apellido = request.form['apellido']
    nombre = request.form['nombre']
    tel = request.form['tel']
    email = request.form['email']
    idtw = request.form['idtw']
    comentario = request.form['comentario']

    if apellido and nombre and tel and email and idtw and comentario:

        cursor = db.cursor()
        sql = "UPDATE lista_cliente SET apellido = %s, nombre = %s, tel = %s, email = %s, idtw = %s, comentario = %s WHERE id = %s"
        data = (apellido, nombre, tel, email, idtw, comentario, id)
        cursor.execute(sql, data)
        db.commit()
    return redirect(url_for('lista_cliente'))

@app.route('/buscador_cliente', methods=['POST']) 
def buscar_cliente():                                           
    db = mysql.connector.connect(
    host='localhost',
    user='crujer',
    password='00arg1428',
    database='test'
    )

    cursor = db.cursor()
    categoria = request.form['categoria']
    buscador = request.form['buscador']
    #cursor.execute("SELECT * FROM users WHERE apellido = '{}'".format(buscador))
    cursor.execute("SELECT * FROM lista_cliente WHERE {} = '{}'".format(categoria,buscador))
    myresult = cursor.fetchall()
    #Convertir los datos a diccionario
    insertObject = []
    columnNames = [column[0] for column in cursor.description]
    for record in myresult:
        insertObject.append(dict(zip(columnNames, record)))
    cursor.close()
    return render_template('lista_cliente.html', data=insertObject)

@app.route('/ordenar_cliente', methods=['POST'])
def ordenar_cliente_desc():
    db = mysql.connector.connect(
    host='localhost',
    user='crujer',
    password='00arg1428',
    database='test'
    )
    
    cursor = db.cursor()
    categoria = request.form['categoria_ordenar']
    estilo = request.form['estilo']

    cursor.execute("SELECT * FROM lista_cliente ORDER BY {} {}".format(categoria, estilo))
    myresult = cursor.fetchall()
    insertObject = []                                                               #Convertir los datos a diccionario
    columnNames = [column[0] for column in cursor.description]
    for record in myresult:
        insertObject.append(dict(zip(columnNames, record)))
    cursor.close()
    return render_template('lista_cliente.html', data=insertObject)

# INICIO Ruta CARRITO DE COMPRAS
@app.route('/carrito_compras')
def carrito_compras():
   return render_template('carrito_compras.html')

# INICIO Ruta UPLOAD
@app.route('/upload', methods=["GET", "POST"])                                      #al decorador de ruta le paso la extension y los metodos GET para mostrar formulario y al ser POST hace otra accion
@login_required                                                                     #loguin necesario, sin hacerlo inhabilita la ruta
def upload():
    if request.method == "POST":                                                    #Si el metodo de respuesta es POST, que haga...
        if "ourfile" not in request.files:                                          # creo la condicion q si no existe en request el archivo ourfile (osea q no se cargue un archivo) o no tenga la terminacion aceptada
            flash("El formulario tiene error")                                      #decimos (devolvemos) que el archivo no es correcto
            return render_template('upload.html')
        file = request.files["ourfile"]                                             #Asignamos una variable y recuperamos el archivo q se mande a travez del input creado en el formulario llamado "ourfile"
                                                                                    #Ahora creamos la condicion cuando no exite ningun archivo pero si se manda el input
        if file.filename == "":
            flash("No selecciono archivo")                                          #decimos (devolvemos) que el archivo no fue seleccionado apra cargar
            return render_template('upload.html')
        if file and allowed_file(file.filename):                                    #Si hay cargado un archivo y ejecuto la funcion def allowed_file con el parametro fiename para saber si la extension es valida, sigue con la carga del archivo
                                                                                    #carpeta_usuario = ("./uploads/{}".format(current_user.fullname))
                                                                                    #filename = secure_filename(file.filename) #en una variable ponemos el nombre del usuario y separado con un espacio el nombre de ese archivo
                                                                                    #filename = secure_filename(current_user.id + '_' + file.filename) #en una variable ponemos el nombre del usuario y separado con un espacio el nombre de ese archivo

            filename = secure_filename(current_user.username + '_' + file.filename) #en una variable ponemos el nombre del usuario y separado con un espacio el nombre de ese archivo
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))          # para guardar el archivo usamos el mettodo save de nuestro mismo objeto y pasamos como parametro la libreria os path join para entrar al acceder al directorio donde se encuentr aalmacenado con la clave UPLOAD_FOLDER, y como segundo paramentro el nombre con el q queremos q se guarde el archivo (la ruta del directorio donde queremos q se guarde + el nombre dle archivo) secure filname chequea si es danino cambia el nombre para q no ejecute nada raro
            return redirect(url_for("get_file", filename=filename))
    return render_template('upload.html')

@app.route("/uploads/<filename>")                                                   #para devolver o recuperar un archivo creamos la ruta y una variable para crear una ruta dinamica
def get_file(filename):                                                             #Asignamos una funcion con la variable dinamica
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)               #(muestra loq  subimos en el navegador) devuelve como respusta lo q de como resultado de usar la funcion send_from_directory y le pasamos como parametro el directorio donde debe acceder y como segundo parametro q archivo debe tomar ahi y lo introduzca a la url <filename>

# INICIO Ruta PERFIL_USUARIO
@app.route('/perfil_usuario')
@login_required 
def perfil_usuario():                                           
    db = mysql.connector.connect(
    host='localhost',
    user='crujer',
    password='00arg1428',
    database='test'
    )

    cursor = db.cursor()
    cursor.execute("SELECT * FROM user WHERE username = '{}'".format(current_user.username))
    myresult = cursor.fetchall()
    insertObject = []
    columnNames = [column[0] for column in cursor.description]
    for record in myresult:
        insertObject.append(dict(zip(columnNames, record)))
    cursor.close()
    return render_template('perfil_usuario.html', info=insertObject)

@app.route('/edit_perfil_usuario/<string:id>', methods=['GET', 'POST'])
def edit_perfil_usuario(id):
    db = mysql.connector.connect(
    host='localhost',
    user='crujer',
    password='00arg1428',
    database='test'
    )  

    username = request.form['username']
    passw = request.form['password']
    password = generate_password_hash(passw)
    fullname = request.form['fullname']
    mail = request.form['mail']
    imagen = request.form['img']
    
    if username and password and fullname and mail and imagen:
        cursor = db.cursor()
        sql = "UPDATE user SET username = %s, password = %s, fullname = %s, mail = %s, img = %s WHERE id = %s"
        info = (username, password, fullname, mail, imagen, id)
        cursor.execute(sql, info)
        db.commit()
    return redirect(url_for('perfil_usuario'))
    
@app.route('/foto_perfil_usuario/<string:id>', methods=["GET", "POST"])             #al decorador de ruta le paso la extension y los metodos GET para mostrar formulario y al ser POST hace otra accion
@login_required                                                                     
def foto_perfilupload(id):
    if request.method == "POST":                                                    #Si el metodo de respuesta es POST, que haga...
        if "ourfile" not in request.files:                                          # creo la condicion q si no existe en request el archivo ourfile (osea q no se cargue un archivo) o no tenga la terminacion aceptada
            flash("El formulario tiene error")                                      #decimos (devolvemos) que el archivo no es correcto
            return render_template('perfil_usuario.html')
        file = request.files["ourfile"]                                             # asignamos una variable y recuperamos el archivo q se mande a travez del input creado en el formulario llamado "ourfile"
                                                                                    #Ahora creamos la condicion cuando no exite ningun archivo pero si se manda el input
        if file.filename == "":
            flash("No selecciono archivo")                                          #decimos (devolvemos) que el archivo no fue seleccionado apra cargar
            return redirect(url_for('perfil_usuario'))
        if file and allowed_file(file.filename):                                    #Si hay cargado un archivo y ejecuto la funcion def allowed_file con el parametro fiename para saber si la extension es valida, sigue con la carga del archivo
                                                                                    #carpeta_usuario = ("./uploads/{}".format(current_user.fullname))
                                                                                    #filename = secure_filename(current_user.fullname + '_' + file.filename) #en una variable ponemos el nombre del usuario y separado con un espacio el nombre de ese archivo

            filename = secure_filename(file.filename)                               #en una variable ponemos el nombre del usuario y separado con un espacio el nombre de ese archivo
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))          # para guardar el archivo usamos el mettodo save de nuestro mismo objeto y pasamos como parametro la libreria os path join para entrar al acceder al directorio donde se encuentr aalmacenado con la clave UPLOAD_FOLDER, y como segundo paramentro el nombre con el q queremos q se guarde el archivo (la ruta del directorio donde queremos q se guarde + el nombre dle archivo) secure filname chequea si es danino cambia el nombre para q no ejecute nada raro

            db = mysql.connector.connect(
            host='localhost',
            user='crujer',
            password='00arg1428',
            database='test'
            )  

            img = filename

            if img:
                cursor = db.cursor()
                sql = "UPDATE user SET img = '{}' WHERE id = {}".format(img, id)
                cursor.execute(sql)
                db.commit()
            return redirect(url_for('perfil_usuario'))                              #hacemos un redireccionamiento a la funcion get_file con el parametro filename
        flash("Extension no permitida")                                             #Si la extension del archivo a cargar no es la correcta muestro el mensaje
        return render_template('perfil_usuario.html')
                                                                                    # importamos os --> (importamos la libreria os para crear una ruta absoluta)
                                                                                    # UPLOAD_FOLDER = os.path.abspath("./uploads/") --> creamos una ruta declarando una nueva variable que sera igual a la ruta absoluta de las librerias y funciones usadas arriba
                                                                                    # app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER --> almacenamos nuestro valor, la ruta absoluta donde queremos q se suban los archivos
                                                                                    # (lo q hace es verificar el archivo q se sube y si es potencialmente danino lo cambia) si hay extensiones de arhicvos q no queremos q se suban porq son potencilmente peligrosos, 1ro debemos valernos del modulo werkzeug (from werkzeug.utils import secure_filename)
                                                                                    # para permitir subir solo ciertos tipos de archivos (extensiones) creamos una variable llamada ALLOWED_EXTENSIONS = set(["png", "jpg", "jpge"]) y setiamos los formatos habilitados

    return render_template('perfil_usuario.html')

@login_required                                                                    
def upload_perfil():
    if request.method == "POST":                                                    #Si el metodo de respuesta es POST, que haga...
        if "ourfile" not in request.files:                                          # creo la condicion q si no existe en request el archivo ourfile (osea q no se cargue un archivo) o no tenga la terminacion aceptada
            flash("El formulario tiene error")                                      #decimos (devolvemos) que el archivo no es correcto
            return render_template('perfil_usuario.html')
        file = request.files["ourfile"]                                             # asignamos una variable y recuperamos el archivo q se mande a travez del input creado en el formulario llamado "ourfile"
        if file.filename == "":                                                     #Ahora creamos la condicion cuando no exite ningun archivo pero si se manda el input
            flash("No selecciono archivo")                                          #decimos (devolvemos) que el archivo no fue seleccionado apra cargar
            return render_template('perfil_usuario.html')
        if file and allowed_file(file.filename):                                    #Si hay cargado un archivo y ejecuto la funcion def allowed_file con el parametro fiename para saber si la extension es valida, sigue con la carga del archivo
                                                                                    #carpeta_usuario = ("./uploads/{}".format(current_user.fullname))
            filename = secure_filename(current_user.fullname + '_' + file.filename) #en una variable ponemos el nombre del usuario y separado con un espacio el nombre de ese archivo
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))          # para guardar el archivo usamos el mettodo save de nuestro mismo objeto y pasamos como parametro la libreria os path join para entrar al acceder al directorio donde se encuentr aalmacenado con la clave UPLOAD_FOLDER, y como segundo paramentro el nombre con el q queremos q se guarde el archivo (la ruta del directorio donde queremos q se guarde + el nombre dle archivo) secure filname chequea si es danino cambia el nombre para q no ejecute nada raro
            return redirect(url_for("get_file", filename=filename))                 #hacemos un redireccionamiento a la funcion get_file con el parametro filename
        flash("Extension no permitida")                                             #Si la extension del archivo a cargar no es la correcta muestro el mensaje
        return redirect(url_for('perfil_usuario'))

# INICIO Ruta AULA VIRTUAl
@app.route('/aula_virtual')
@login_required 
def aula_virtual():
   return render_template('aula_virtual.html')

# INICIO Ruta CONTACTO
@app.route('/contacto')
def contacto():
   return render_template('contacto.html')

@app.route('/protected')                                                            #me hace logearme para acceder
@login_required 
def protected():
   return "<h1>Esta es una vista protegida, solo para usuarios logeados</h1>"

def status_401(error):                                                              #si detecta un error redirige al login porq la peticion no se ejecuto
    return redirect(url_for('login'))

def status_404(error):                                                              #si detecta q se intento acceder a url q no existerror
    return"<h1>Página no encontrada</h1>", 404

if __name__ == '__main__':
    app.config.from_object(config['development'])
    app.register_error_handler(401,status_401)
    app.register_error_handler(404,status_404)
    app.run(debug=True, port=5000)