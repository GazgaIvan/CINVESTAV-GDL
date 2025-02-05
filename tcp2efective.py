import socket
import threading
import firebase_admin
from firebase_admin import credentials, firestore

# 🔥 Configurar Firebase Firestore
cred = credentials.Certificate(r"D:\Info\Documentos\UTVCO\ME1101\CINVESTAV\ggirprueba2-firebase-adminsdk-fbsvc-3c9651eed7.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# 🔧 Configuración del servidor
HOST = '192.168.1.104'  # Dirección local
PORT = 65432            # Puerto

# Lista de hilos activos
active_threads = []

def save_to_firestore(data, addr):
    """Guarda los datos recibidos en Firestore."""
    try:
        # Dividir el mensaje en dos partes: "recamara" y la fecha y hora
        if "fecha y hora:" in data:
            message_parts = data.split("fecha y hora:")
            recamara = message_parts[0].strip()  # "recamara"
            timestamp = message_parts[1].strip()  # La fecha y hora

            # Guardar en Firestore
            db.collection("datos_recibidos").add({
                "ip": addr[0],
                "mensaje": recamara,
                "timestamp": timestamp
            })
            print(f"Datos guardados en Firestore: Recamara: {recamara}, Fecha y Hora: {timestamp} desde {addr}")
        else:
            print("Formato de mensaje incorrecto o no contiene 'fecha y hora'")
    except Exception as e:
        print(f"Error al guardar en Firestore: {e}")

def handle_client(conn, addr):
    """Maneja la comunicación con un cliente manteniendo la conexión abierta."""
    print(f"Conexión establecida con {addr}")
    try:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            mensaje = data.decode().strip()
            print(f"Mensaje recibido de {addr}: {mensaje}")

            # Guardar en Firestore solo si el mensaje no está vacío
            if mensaje:
                save_to_firestore(mensaje, addr)

            # Responder al cliente
            conn.sendall(f"Mensaje recibido: {mensaje}".encode())
    except ConnectionResetError:
        print(f"El cliente {addr} cerró la conexión abruptamente.")
    finally:
        conn.close()
        print(f"Conexión cerrada con {addr}")

        # Eliminar el hilo del cliente desconectado
        global active_threads
        active_threads = [t for t in active_threads if t.is_alive()]  # Eliminar hilos inactivos
        print(f"Hilos activos restantes: {len(active_threads)}")

def start_server():
    """Inicializa y ejecuta el servidor TCP."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.bind((HOST, PORT))
            server_socket.listen(5)
            print(f"Servidor escuchando en {HOST}:{PORT}")

            # Limpiar cualquier hilo previo que haya quedado
            global active_threads
            active_threads = []

            while True:
                conn, addr = server_socket.accept()

                # Crear un nuevo hilo para cada cliente y agregarlo a la lista de hilos activos
                client_thread = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
                active_threads.append(client_thread)  # Agregar hilo a la lista
                client_thread.start()

                print(f"Hilos activos: {len(active_threads)}")
    except OSError as e:
        print(f"Error en el servidor: {e}")
    except KeyboardInterrupt:
        print("\nServidor detenido manualmente.")
    finally:
        print("Servidor cerrado.")

if __name__ == "__main__":
    start_server()
