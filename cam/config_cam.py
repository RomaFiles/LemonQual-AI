import cv2
import configparser
import time
import os

# Inicializa el lector de configuración con manejo de errores
config = configparser.ConfigParser()
config_file = 'cameras.ini'

# Alerta de fallo al no encontrar archivo de configuración de cámaras
if not os.path.exists(config_file):
    raise FileNotFoundError(f"El archivo de configuración '{config_file}' no existe.")

# Lee el archivo de configuración
config.read(config_file)

# Obtener las URLs de las cámaras y crear un diccionario con sus nombres
try:
    camera_urls = {
        section: config[section]['url'] 
        for section in config.sections() if 'url' in config[section]
    }
except KeyError as e:
    raise KeyError(f"Falta una clave 'url' en una sección del archivo de configuración: {e}")

# Inicializar el diccionario de cámaras iterativamente (sin verificación inicial)
cameras = {
    name: cv2.VideoCapture(url) for name, url in camera_urls.items()
}

# Configurar el tamaño del buffer para cada cámara
for name, cam in cameras.items():
    cam.set(cv2.CAP_PROP_BUFFERSIZE, 1)

# Función para reconectar cámaras
def reconnect_camera(name, cam, url):
    """Intenta reconectar una cámara."""
    print(f"Intentando reconectar {name}...")
    cam.release()  # Libera los recursos actuales
    cam.open(url)  # Intenta reconectar con la URL
    cam.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Configura el buffer

    # Verifica si la reconexión fue exitosa
    if cam.isOpened():
        print(f"{name} se reconectó exitosamente.")
        return True
    else:
        print(f"{name} falló al reconectar.")
        return False
    
# FALTA ACTUALIZAR LA FUNCIÓN INIT_CAM CON CUDA

# Función para verificar que las cámaras estén conectadas
def init_cam():
    """Intenta conectar todas las cámaras. Reintenta en caso de fallo."""
    while True:
        # Rastrea el estado de las cámaras
        estados = {"conectadas": [], "fallidas": []}
        
        for name, cam in cameras.items():
            if cam.isOpened():
                estados["conectadas"].append(name)
            else:
                if reconnect_camera(name, cam, camera_urls[name]):
                    estados["conectadas"].append(name)
                else:
                    estados["fallidas"].append(name)

        # Mostrar el estado actual
        print("\n--- Estado de las cámaras ---")
        print(f"Conectadas: {estados['conectadas']}")
        print(f"Fallidas: {estados['fallidas']}\n")

        # Si todas están conectadas, salimos del loop
        if not estados["fallidas"]:
            print("Todas las cámaras están conectadas.")
            return True
        
        # Espera antes de intentar de nuevo
        time.sleep(2)

# Función para mostrar video
def show_video():
    """Muestra el video de todas las cámaras en ventanas separadas."""
    print("Mostrando video. Presiona 'q' para salir.")

    # Crear las ventanas antes del bucle
    for name in cameras.keys():
        cv2.namedWindow(name, cv2.WINDOW_NORMAL)  # Ventanas ajustables
    prev_time = time.time()
    try:
        while True:
            for name, cam in cameras.items():
                if cam.isOpened():
                    # Registrar el tiempo antes de leer el frame
                    start_time = time.time()
                    ret, frame = cam.read()
                    if ret:
                        # Registrar el tiempo después de leer el frame
                        end_time = time.time()
                        # Latencia en milisegundos
                        latency = (end_time - start_time) * 1000
                        # Obtener resolución del video
                        height, width, _ = frame.shape
                        resolution_text = f"Resolucion: {width}x{height}"

                        # Medir FPS
                        curr_time = time.time()
                        fps = 1 / (curr_time - prev_time)
                        prev_time = curr_time

                        # Preparar el texto para mostrar
                        id_text = f"ID: {name}"
                        fps_text = f"FPS: {fps:.2f}"
                        latency_text = f"Latencia: {latency:.2f} ms"
                        
                        # Superponer ID y resolución en la esquina superior izquierda
                        cv2.putText(frame, id_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 1, cv2.LINE_AA)
                        cv2.putText(frame, resolution_text, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 1, cv2.LINE_AA)
                        cv2.putText(frame, fps_text, (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 1, cv2.LINE_AA)
                        cv2.putText(frame, latency_text, (400, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 1, cv2.LINE_AA)


                        # Procesamiento con CUDA
                        try:
                            # Cargar el frame en la GPU
                            gpu_frame = cv2.cuda_GpuMat()
                            gpu_frame.upload(frame)

                            # Aquí podrías realizar otros procesos, pero dejamos el frame en color
                            # La línea de abajo convierte el frame a escala de grises, pero estará desactivada por ahora
                            # gpu_gray = cv2.cuda.cvtColor(gpu_frame, cv2.COLOR_BGR2GRAY)

                            # Descargar el frame procesado de nuevo a la CPU
                            frame = gpu_frame.download()
                        except Exception as e:
                            print(f"Error con CUDA en {name}: {e}")
                            # En caso de fallo, muestra el frame original
                            pass


                        # Mostrar el frame procesado
                        cv2.imshow(name, frame)
                    else:
                        print(f"No se pudo leer el cuadro de {name}. Reintentando...")
                        cam.release()
                        cam.open(camera_urls[name])  # Reintenta abrir si falla
                else:
                    print(f"{name} no está conectada.")

            # Salir con la tecla 'q'
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("Cerrando...")
                break

    except Exception as e:
        print(f"Error en el loop de video: {e}")

    finally:
        # Liberar recursos después de salir
        for name, cam in cameras.items():
            print(f"Liberando {name}...")
            cam.release()
        cv2.destroyAllWindows()