import tkinter as tk
import firebase_admin
from firebase_admin import credentials, firestore
import threading
from PIL import Image, ImageTk  # Importamos Pillow para manipular imágenes
import time

# Inicializa Firebase
cred = credentials.Certificate('D:/Info/Documentos/UTVCO/ME1101/CINVESTAV/ggirprueba2-firebase-adminsdk-fbsvc-3c9651eed7.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

# Posiciones de las habitaciones con etiquetas
target_positions = {
    "cocina": (70, 60),
    "sala": (190, 60),
    "gym": (310, 60),
    "comedor": (130, 190),
    "recamara": (250, 190)
}

class HomeSimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulador de Casa")
        self.canvas = tk.Canvas(root, width=400, height=300, bg="lightgray")
        self.canvas.pack()
       
        self.draw_rooms()
       
        # Cargar imagen del robot simpático
        self.robot_image = Image.open("Goku-png.png")  # Asegúrate de tener una imagen llamada robot_image.png
        self.robot_image = self.robot_image.resize((50, 50))  # Redimensionar la imagen para ajustarla
        self.robot_photo = ImageTk.PhotoImage(self.robot_image)
       
        # Iniciar hilo para escuchar cambios en la base de datos
        threading.Thread(target=self.listen_for_updates, daemon=True).start()
   
    def draw_rooms(self):
        # Dibujar separaciones y etiquetas
        self.canvas.create_rectangle(20, 20, 120, 120, outline="black")  # Cocina
        self.canvas.create_text(70, 10, text="Cocina")
       
        self.canvas.create_rectangle(140, 20, 240, 120, outline="black")  # Sala
        self.canvas.create_text(190, 10, text="Sala")
       
        self.canvas.create_rectangle(260, 20, 360, 120, outline="black")  # Gym
        self.canvas.create_text(310, 10, text="Gym")
       
        self.canvas.create_rectangle(80, 140, 180, 240, outline="black")  # Comedor
        self.canvas.create_text(130, 130, text="Comedor")
       
        self.canvas.create_rectangle(200, 140, 300, 240, outline="black")  # Recámara
        self.canvas.create_text(250, 130, text="Recámara")
   
    def listen_for_updates(self):
        def on_snapshot(col_snapshot, changes, read_time):
            for change in changes:
                # Obtener la ubicación actualizada
                last_location = change.document.to_dict().get("mensaje")

                # Si es un documento nuevo o un documento modificado, actualizar la interfaz
                if change.type.name in ['ADDED', 'MODIFIED']:
                    print(f"Ubicación detectada ({change.type.name}): {last_location}")
                    if last_location in target_positions:
                        self.root.after(0, lambda: self.mark_room(last_location))

        # Referencia a la colección
        usuarios_ref = db.collection('datos_recibidos')
        usuarios_ref.on_snapshot(on_snapshot)
   
    def mark_room(self, room):
        self.canvas.delete("robot")
        x, y = target_positions[room]
       
        # Mostrar la imagen del robot simpático en la posición correspondiente
        self.canvas.create_image(x, y, image=self.robot_photo, tags="robot")

if __name__ == "__main__":
    root = tk.Tk()
    app = HomeSimulator(root)
    root.mainloop()