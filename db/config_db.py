import psycopg2
from configparser import ConfigParser
import time
import sys

# Si no se usa la ruta absoluta, por alguna razon no encuentra la seccion del database.ini (No tiene sentido el erro, es estupido)
def config(filename="/home/cc-frutas/Documentos/LemonQual AI/db/database.ini", section="main"):

    # Crear un parser
    parser = ConfigParser()
    # Leer archvivo de configuración
    parser.read(filename)
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] =param[1]
    else:
        raise Exception('Section{0} is not found in the {1} file'.format(section, filename))
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