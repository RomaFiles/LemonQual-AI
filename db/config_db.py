import psycopg2
from configparser import ConfigParser
import os
import time
import sys

def config(filename="database.ini", section ="main"):
    # Obtener la ruta absoluta del archivo de configuración
    filepath = os.path.join(os.path.dirname(__file__), filename)

    # Crear un parser
    parser = ConfigParser()
    
    # Leer archivo de configuración
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"El archivo '{filename}' no existe en la ruta '{filepath}'.")
    parser.read(filepath)

    # Obtener los parámetros de la sección especificada
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] =param[1]
    else:
        raise Exception(f"La sección '{section}' no se encuentra en el archivo '{filename}'.")
    return db

def connect(max_attempts=5):
    # Contador de intentos
    attempts = 0
    connection = None
    while attempts < max_attempts:
        try:
            # Obtenemos los parámetros de conexión desde el archivo de configuración
            params = config()
            print('Conectando a base de datos.')
            
            # Se intenta conectar a la base de datos
            connection = psycopg2.connect(**params)

            # Crear un cursor y verifica la conexión
            crsr = connection.cursor()
            crsr.execute('SELECT version()')
            db_version = crsr.fetchone()
            print(f'Conexión exitosa a la base de datos. Versión: {db_version}')
            crsr.close()
            return connection # Retorna conexión exitosa
        
        except(Exception, psycopg2.DatabaseError) as error:
            attempts += 1
            print(f"Error en la conexión {error}")

            if attempts < max_attempts:
                print("Reintentando.")
                time.sleep(2)
            else:
                print("Se alcanzó el número máximo de intentos fallidos. Saliendo.")
                sys.exit(1) # Termina el programa si fallan todos los intentos.
    return connection

connection = connect()