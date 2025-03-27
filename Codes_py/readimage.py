import serial
from PIL import Image  # Importer la bibliothèque Pillow

# Configurez le port série et le débit en bauds
ser = serial.Serial('COM3', 460800)  # Remplacez 'COM3' par le port série de votre Arduino
ser.flushInput()

# Dimensions de l'image
width = 320
height = 240

num = 1
while 1:
    # Attendre le signal "PHOTO"
    print("En attente du signal 'PHOTO'...")
    while True:
        if ser.in_waiting > 0:
            try:
                line = ser.readline().decode('utf-8').strip()  # Lire une ligne et la décoder
                print(line)
                if line == "PHOTO":
                    print("Signal 'PHOTO' détecté. Début de la lecture des données...")
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

    print("Données reçues !")

    # Créer une image en niveaux de gris avec Pillow
    img_lum = Image.new('L', (width, height))  # 'L' pour niveaux de gris
    img_lum.putdata(frame_lum)  # Ajouter les données de luminance

    # Enregistrer l'image de luminance
    img_lum.save(f"img/image{num}.png")  # Enregistrer l'image
    print(f"Image de luminance enregistrée sous le nom 'image{num}.png'.")

    num += 1

ser.close()
