import cv2
import os

# Définir les dossiers source et destination dans le même dossier que le script
input_folder = './old'
output_folder = './new'

# Créer les dossiers s'ils n'existent pas
os.makedirs(input_folder, exist_ok=True)
os.makedirs(output_folder, exist_ok=True)

# Paramètres initiaux du crop (modifiable avec les flèches)
crop_x, crop_y = 50, 50
crop_w, crop_h = 240, 320  # Taille fixe avec un ratio 4:3

# Sensibilité des déplacements
delta_move = 10

# Nom de l'image à partir de laquelle reprendre (laisser vide pour commencer au début)
start_image = "Poire_Test13"  # Remplacez par le nom de l'image ou laissez vide

def crop_images():
    global crop_x, crop_y, crop_w, crop_h
    
    # Liste des fichiers images
    files = [f for f in os.listdir(input_folder) if f.lower().endswith(('png', 'jpg', 'jpeg'))]
    
    # Trouver l'index de l'image de départ
    if start_image and start_image in files:
        start_index = files.index(start_image) + 1
    else:
        start_index = 0  # Si l'image n'est pas trouvée ou si start_image est vide, commencer au début

    for file in files[start_index:]:
        image_path = os.path.join(input_folder, file)  # Utilisation de chemins relatifs
        
        img = cv2.imread(image_path)
        
        if img is None:  # Vérifier si l'image est chargée
            print(f"Erreur : Impossible de charger l'image '{image_path}'. Vérifiez le chemin ou l'intégrité du fichier.")
            continue
        
        h, w, _ = img.shape
        
        while True:
            img_copy = img.copy()
            # Dessiner le rectangle de crop
            cv2.rectangle(img_copy, (crop_x, crop_y), (crop_x + crop_w, crop_y + crop_h), (0, 255, 0), 2)
            cv2.imshow('Cropping Tool', img_copy)
            
            key = cv2.waitKey(0) & 0xFF
            
            if key == 27:  # Échap pour quitter
                cv2.destroyAllWindows()
                return
            elif key == ord('w'):  # Quitter sans enregistrer
                break
            elif key == 13:  # Entrée pour valider le crop
                cropped = img[crop_y:crop_y + crop_h, crop_x:crop_x + crop_w]
                resized = cv2.resize(cropped, (crop_w, crop_h))  # Redimensionner l'image
                cv2.imwrite(os.path.join(output_folder, file), resized)
                break
            elif key == ord('z'):  # Touche 'z' pour monter
                crop_y = max(0, crop_y - delta_move)  # Empêcher de dépasser le bord supérieur
                print(f"Rectangle déplacé vers le haut : crop_x={crop_x}, crop_y={crop_y}")
            elif key == ord('s'):  # Touche 's' pour descendre
                crop_y = min(h - crop_h, crop_y + delta_move)  # Empêcher de dépasser le bord inférieur
                print(f"Rectangle déplacé vers le bas : crop_x={crop_x}, crop_y={crop_y}")
            elif key == ord('q'):  # Touche 'q' pour aller à gauche
                crop_x = max(0, crop_x - delta_move)  # Empêcher de dépasser le bord gauche
                print(f"Rectangle déplacé vers la gauche : crop_x={crop_x}, crop_y={crop_y}")
            elif key == ord('d'):  # Touche 'd' pour aller à droite
                crop_x = min(w - crop_w, crop_x + delta_move)  # Empêcher de dépasser le bord droit
                print(f"Rectangle déplacé vers la droite : crop_x={crop_x}, crop_y={crop_y}")
            elif key == ord('a'):  # Touche 'a' pour diminuer la taille du rectangle
                new_crop_w = max(10, crop_w - delta_move)  # Empêcher une largeur trop petite
                new_crop_h = int(new_crop_w * 4 / 3)  # Ajuster la hauteur pour conserver le ratio 4:3
                if crop_x + new_crop_w <= w and crop_y + new_crop_h <= h:  # Vérifier les limites
                    crop_w, crop_h = new_crop_w, new_crop_h
                print(f"Taille du rectangle diminuée : crop_w={crop_w}, crop_h={crop_h}")
            elif key == ord('e'):  # Touche 'e' pour augmenter la taille du rectangle
                new_crop_w = min(w - crop_x, crop_w + delta_move)  # Empêcher de dépasser la largeur de l'image
                new_crop_h = int(new_crop_w * 4 / 3)  # Ajuster la hauteur pour conserver le ratio 4:3
                if crop_x + new_crop_w <= w and crop_y + new_crop_h <= h:  # Vérifier les limites
                    crop_w, crop_h = new_crop_w, new_crop_h
                print(f"Taille du rectangle augmentée : crop_w={crop_w}, crop_h={crop_h}")
            
        cv2.destroyAllWindows()

if __name__ == "__main__":
    crop_images()