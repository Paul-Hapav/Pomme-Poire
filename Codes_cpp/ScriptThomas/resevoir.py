import serial
from PIL import Image  # Importer la bibliothèque Pillow

# Configurez le port série et le débit en bauds
ser = serial.Serial('COM4', 460800)  # Remplacez 'COM3' par le port série de votre Arduino
ser.flushInput()

# Dimensions de l'image
width = 320
height = 240

num = 1
while 1:
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

    print("En attente du signal 'COULEUR'...")
    while True:
        try:
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8').strip()  # Lire une ligne et la décoder
                print(line)
                if line == "COULEUR":
                    print("Signal 'COULEUR' détecté. Début de la lecture des données...")
                    break
        except:
            pass

    # Lire les données de chromatique
    frame_col = []
    try:
        while len(frame_col) < width * height:  # 1 octet par pixel pour chromatique (U et V combinés)
            if ser.in_waiting > 0:
                data = ser.read()  # Lire un octet
                frame_col.append(ord(data))  # Convertir en entier (0-255)

    except KeyboardInterrupt:
        print("Interruption par l'utilisateur.")

    print("Données reçues !")

    # Convertir les données en une image couleur
    index = 0
    dataCb = list()
    dataCr = list()
    bitmap = list()
    Alt = True

    for chroma in frame_col:
        if Alt:
            dataCr.extend([chroma,chroma])
            Alt = False
        else:
            dataCb.extend([chroma,chroma])
            Alt = True



    for y in range(height):
        for x in range(width):
            Y = frame_lum[index]
            Cb = dataCb[index]
            Cr = dataCr[index]

            R = int(max(0, min(255,Y + 1.40200 * (Cr - 0x80))))
            G = int(max(0, min(255,Y - 0.34414 * (Cb - 0x80) - 0.71414 * (Cr - 0x80))))
            B = int(max(0, min(255,Y + 1.77200 * (Cb - 0x80))))
            bitmap.append((R,G,B))
            index += 1

    # Créer une image en couleur avec Pillow
    img = Image.new('RGB', (width, height))  # 'RGB' pour image couleur
    img.putdata(bitmap)  # Ajouter les données de l'image
    img.save(f"image/col/image_recue_couleur_{num}.png")  # Enregistrer l'image au format PNG
    print(f"Image enregistrée sous le nom 'image_recue_couleur_{num}.png'.")

    img_col = Image.new('L', (width, height))  # 'L' pour niveaux de gris
    img_col.putdata(frame_col)  # Ajouter les données de chromatique
    img_col.save(f"image/chro/image_chromatique_{num}.png")  # Enregistrer l'image
    print(f"Image de chromatique enregistrée sous le nom 'image_chromatique_{num}.png'.")

    img_lum = Image.new('L', (width, height))  # 'L' pour niveaux de gris
    img_lum.putdata(frame_lum)  # Ajouter les données de luminance
    img_lum.save(f"image/lum/image_luminance_{num}.png")  # Enregistrer l'image
    print(f"Image de chromatique enregistrée sous le nom 'image_chromatique_{num}.png'.")
    num+=1

ser.close()

