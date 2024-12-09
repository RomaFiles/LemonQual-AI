import configparser
import cv2

# Función para cargar la configuración de las cámaras
def load_camera_config(config_file):
    """
    Carga la configuración de las cámaras desde un archivo .ini.
    
    Args:
        config_file (str): Ruta al archivo de configuración .ini.
        
    Returns:
        dict: Diccionario con nombres de cámaras como claves y URLs como valores.
    """
    config = configparser.ConfigParser()
    config.read(config_file)

    cameras = {}
    for section in config.sections():
        if 'url' in config[section]:
            cameras[section] = config[section]['url']
    return cameras

# Función para capturar un fotograma de una cámara específica
def capture_frame(camera_url):
    """
    Captura un fotograma desde la cámara con la URL especificada.
    
    Args:
        camera_url (str): URL de la cámara (RTSP, etc.).
        
    Returns:
        frame: Fotograma capturado como matriz de imagen.
    """
    cap = cv2.VideoCapture(camera_url)
    if not cap.isOpened():
        raise Exception(f"No se pudo abrir la cámara en {camera_url}")

    ret, frame = cap.read()
    cap.release()

    if not ret:
        raise Exception(f"No se pudo capturar el fotograma de {camera_url}")
    
    return frame
