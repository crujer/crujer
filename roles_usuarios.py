# -*- coding: utf-8 -*-
import os
import csv
import re
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, abort
from flask_login import (
    current_user, login_user, logout_user,
    login_required, LoginManager, UserMixin
)
from peewee import *


app = Flask(__name__)
app.secret_key = b'Zlnkkmv37di0aV3f'
login_manager = LoginManager()
login_manager.init_app(app)

#--------- BASE DE DATOS ---------#

db = PostgresqlDatabase('roles_db', user='mibase', password='mibase',
    host='localhost', port=5432, autorollback=True)

class BaseModel(Model):
    class Meta:
        database = db

class Users(UserMixin, BaseModel):
    id = AutoField()
    username = CharField(max_length=1024)
    password = CharField(max_length=1024)
    email = CharField(max_length=1024)
    
    @login_manager.user_loader
    def load_user(user_id):
        for user in Users:
            if user.id == int(user_id):
                return user
        return None
    
    def load_data():
        path_data_file = os.path.join('data', 'users.csv')
        data = []
        with open(path_data_file) as csv_file:
            dict_file = csv.DictReader(csv_file, delimiter=';')
            for l in dict_file:
                data.append(dict(l))
        for d in data:
            rec = Users.get_or_none(Users.username == d['username'])
            if rec is None:
                Users.create(**d)

class Role(BaseModel):
    id = AutoField()
    name = CharField(max_length=1024)
    code = CharField(max_length=1024)
    
    def load_data():
        path_data_file = os.path.join('data', 'roles.csv')
        data = []
        with open(path_data_file) as csv_file:
            dict_file = csv.DictReader(csv_file, delimiter=';')
            for l in dict_file:
                data.append(dict(l))
        for d in data:
            rec = Role.get_or_none(Role.code == d['code'])
            if rec is None:
                Role.create(**d)

class UserInRole(BaseModel):
    user_id = ForeignKeyField(Users, null=True)
    role_id = ForeignKeyField(Role, null=True)
    
    def load_data():
        path_data_file = os.path.join('data', 'userinrole.csv')
        data = []
        with open(path_data_file) as csv_file:
            dict_file = csv.DictReader(csv_file, delimiter=';')
            for l in dict_file:
                data.append(dict(l))
        for d in data:
            rec = UserInRole.get_or_none(UserInRole.user_id == d['user_id'], UserInRole.role_id == d['role_id'])
            if rec is None:
                UserInRole.create(**d)
    
    class Meta:
        indexes = (
            (('user_id', 'role_id'), True),
        )

#--------- Carga de datos en tablas ---------#
db.create_tables([Users, Role, UserInRole], safe=True)
Users.load_data()
Role.load_data()
UserInRole.load_data()

#--------- CHECK ROLES ---------#
def check_role(roles):    # Declaración del decorador
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for r in roles:
                is_role = Role.get_or_none(Role.code == r)
                if is_role is not None:
                    is_user = UserInRole.get_or_none(UserInRole.role_id == is_role.id, 
                        UserInRole.user_id == current_user.id)
                    if is_user is not None:
                        return func(*args, **kwargs)
            abort(403)
        return wrapper
    return decorator

#--------- SISTEMA ---------#

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET','POST'])
def login():
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = Users.get_or_none(Users.username == username)
        if user != None and user.password == password:
            login_user(user, user.email)
            return redirect(url_for('system'))
    
    return render_template('login.html')

@app.route('/system')
@login_required
@check_role(['user'])    # Llamada del decorador
def system():
    return render_template('system.html')

@app.route('/seccion_1')
@login_required
@check_role(['admin'])
def seccion_1():
    return render_template('web_sys_1.html')

@app.route('/seccion_2')
@login_required
@check_role(['user','admin','manager'])
def seccion_2():
    return render_template('web_sys_2.html')

@app.get('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

#--------- Arranque del sistema ---------#
app.run(host='0.0.0.0', port='8080', debug=True)