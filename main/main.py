import numpy as np
import threading as th
import os
import sys

# Agrega la carpeta raíz al sys.path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(root_dir)
from cam.config_cam import show_video, init_cam
from db.config_db import connect


def main():
    print("Iniciando configuración de cámaras.")
    
    # Inicializa las cámaras
    if init_cam():
        print("Cámaras inicializadas correctamente.")
        
        # Ejecuta `show_video` en un hilo separado
        video_thread = th.Thread(target=show_video, daemon=True)
        video_thread.start()

        # Ejecuta la conexión a la base de datos
        connection = connect()
        if connection:
            print("Conexión a la base de datos exitosa.")

        # Espera a que el hilo de video termine (si es necesario, opcional)
        video_thread.join()
        print("Programa finalizado.")
    else:
        print("Fallo al inicializar cámaras.")

if __name__ == "__main__":
    main()