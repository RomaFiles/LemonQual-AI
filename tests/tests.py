from cam.camera_utils import load_camera_config, capture_frame  # Asegúrate de que estas funciones estén bien definidas

# Ruta al archivo .ini con la configuración de las cámaras
camera_config_file = "../cam/cameras.ini"  # O usa la ruta completa si el archivo está en otro directorio

# Cargar configuraciones de cámaras desde el archivo .ini
cameras = load_camera_config(camera_config_file)

# Probar la captura de cada cámara
for camera_name, camera_url in cameras.items():
    try:
        print(f"Intentando capturar de {camera_name}...")
        frame = capture_frame(camera_url)  # La función capture_frame debe recibir la URL de la cámara
        print(f"Fotograma capturado de {camera_name}")
    except Exception as e:
        print(f"Error con {camera_name}: {e}")
