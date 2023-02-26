import mysql.connector

class Config:
    SECRET_KEY = 'B!1w8NAt1T^%kvhUI*S^' #llave privada para manejar datos de sesion

class DevelopmentConfig(Config):      #la clase config es heredada
    DEBUG = True
    MYSQL_HOST = 'localhost'        
    MYSQL_USER = 'crujer'             #Usuario q estoy usando
    MYSQL_PASSWORD = '00arg1428'    #Password de la DB
    MYSQL_DB = 'test'               #Nombre d ela DB

config = {
    'development': DevelopmentConfig
}

