import socket
import threading
import firebase_admin
from firebase_admin import credentials, firestore
import re  # Para usar expresiones regulares

# 🔥 Configurar Firebase Firestore
cred = credentials.Certificate("D:/Info/Documentos/UTVCO/ME1101/CINVESTAV/ggirprueba2-firebase-adminsdk-fbsvc-3c9651eed7.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# 🔧 Configuración del servidor
HOST = '192.168.0.177'  # Dirección local
PORT = 65432            # Puerto

def save_to_firestore(data, addr):
    """Guarda los datos recibidos en Firestore, separando mensaje y timestamp."""
    try:
        # Usamos una expresión regular para extraer la fecha y hora del mensaje
        match = re.search(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})", data)
        if match:
            fecha_hora = match.group(1)  # Extraemos la fecha y hora
        else:
            fecha_hora = None

        # Guardamos en Firestore
        db.collection("datos_recibidos").add({
            "ip": addr[0],
            "puerto": addr[1],
            "mensaje": data,  # Guardamos el mensaje completo
            "timestamp": fecha_hora if fecha_hora else firestore.SERVER_TIMESTAMP  # Usamos fecha y hora si se extrajo
        })
        print(f"Datos guardados en Firestore: {data} desde {addr}")
    except Exception as e:
        print(f"Error al guardar en Firestore: {e}")

def handle_client(conn, addr):
    """Maneja la comunicación con un cliente manteniendo la conexión abierta."""
    print(f"Conexión establecida con {addr}")
    try:
        while True:
            data = conn.recv(1024)  # Espera datos sin cerrar la conexión
            if not data or data.strip() == b"":  # Ignorar mensajes vacíos
                continue  

            mensaje = data.decode().strip()
            print(f"Mensaje recibido de {addr}: {mensaje}")

            # 🔥 Guardar en Firestore solo si el mensaje no está vacío
            if mensaje:
                save_to_firestore(mensaje, addr)

            # Responder al cliente
            conn.sendall(f"Mensaje recibido: {mensaje}".encode())
    except ConnectionResetError:
        print(f"El cliente {addr} cerró la conexión abruptamente.")
    finally:
        conn.close()
        print(f"Conexión cerrada con {addr}")

def start_server():
    """Inicializa y ejecuta el servidor TCP."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.bind((HOST, PORT))
            server_socket.listen(5)
            print(f"Servidor escuchando en {HOST}:{PORT}")

            while True:
                conn, addr = server_socket.accept()
                client_thread = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
                client_thread.start()
    except OSError as e:
        print(f"Error en el servidor: {e}")
    except KeyboardInterrupt:
        print("\nServidor detenido manualmente.")

if __name__ == "__main__":
    start_server()
