import serial
from PIL import Image  # Importer la bibliothèque Pillow
import numpy as np

# Configurez le port série et le débit en bauds
ser = serial.Serial('COM5', 460800)  # Remplacez 'COM3' par le port série de votre Arduino
ser.flushInput()

# Dimensions de l'image
width = 320
height = 240

num = 1

while True:
    # Attendre le signal "debut"
    print("En attente du signal 'READY'...")
    while True:
        if ser.in_waiting > 0:
            try:
                line = ser.readline().decode('utf-8').strip()  # Lire une ligne et la décoder
                print(line)
                if line == "READY":
                    print("Signal 'READY' détecté. Début de la lecture des données...")
                    break
            except:
                pass

        # Lire les données de luminance
    frame_lum = []
    try:
        while len(frame_lum) < width * height:
            if ser.in_waiting > 0:
                data = ser.read()  # Lire un octet
                frame_lum.append(ord(data))  # Convertir en entier (0-255)

    except KeyboardInterrupt:
            print("Interruption par l'utilisateur.")
            exit(-1)

    img_lum = Image.new('L', (width, height))  # 'L' pour niveaux de gris
    img_lum.putdata(frame_lum)  # Ajouter les données de luminance
    img_lum.save(f"image/lum/image_luminance_{num}.png")  # Enregistrer l'image
    print(f"Image de chromatique enregistrée sous le nom 'image_luminance_{num}.png'.")
    num+=1

""" 
    img_lum = img_lum.convert('RGB')  # Convertir en image RG
    img_lum = img_lum.resize((80, 106))

    # Convertir en tableau NumPy 2D
    img_array = np.array(img_lum) / 255
    img_array = np.expand_dims(img_array, axis=0)  # Devient (1, 106, 80, 3)

    output = model.predict(img_array)
    print("Prédiction :", output)  
"""
ser.close()