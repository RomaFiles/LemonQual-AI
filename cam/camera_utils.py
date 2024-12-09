import cv2

def capture_frame(camera_index=0):
    """
    Captura un fotograma desde la cámara especificada.

    Args:
        camera_index (int): Índice de la cámara a usar. Por defecto, 0.
    
    Returns:
        tuple: Retorna un estado booleano de éxito y el fotograma capturado.
    """
    # Inicializamos la captura de video
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        print(f"Error: No se puede acceder a la cámara {camera_index}.")
        return False, None

    # Leemos un fotograma
    success, frame = cap.read()
    cap.release()  # Liberamos la cámara inmediatamente después de capturar
    
    if not success:
        print("Error: No se pudo capturar el fotograma.")
        return False, None

    return True, frame
