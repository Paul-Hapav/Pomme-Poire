import cv2
import os

# Définir les dossiers source et destination dans le même dossier que le script
script_dir = os.path.dirname(os.path.abspath(__file__))
input_folder = os.path.join(script_dir, 'old')
output_folder = os.path.join(script_dir, 'new')

# Créer les dossiers s'ils n'existent pas
os.makedirs(input_folder, exist_ok=True)
os.makedirs(output_folder, exist_ok=True)

# Paramètres initiaux du crop (modifiable avec les flèches)
crop_x, crop_y = 50, 50
crop_w, crop_h = 200, 200  # Taille fixe

# Sensibilité des déplacements
delta_move = 10

def crop_images():
    global crop_x, crop_y
    
    # Liste des fichiers images
    files = [f for f in os.listdir(input_folder) if f.lower().endswith(('png', 'jpg', 'jpeg'))]
    
    for file in files:
        image_path = os.path.join(input_folder, file)
        img = cv2.imread(image_path)
        h, w, _ = img.shape
        
        while True:
            img_copy = img.copy()
            cv2.rectangle(img_copy, (crop_x, crop_y), (crop_x + crop_w, crop_y + crop_h), (0, 255, 0), 2)
            cv2.imshow('Cropping Tool', img_copy)
            
            key = cv2.waitKey(0) & 0xFF
            
            if key == 27:  # Échap pour quitter
                cv2.destroyAllWindows()
                return
            elif key == ord('q'):  # Quitter sans enregistrer
                break
            elif key == 13:  # Entrée pour valider le crop
                cropped = img[crop_y:crop_y + crop_h, crop_x:crop_x + crop_w]
                cv2.imwrite(os.path.join(output_folder, file), cropped)
                break
            elif key == 82:  # Flèche haut
                crop_y = max(0, crop_y - delta_move)
            elif key == 84:  # Flèche bas
                crop_y = min(h - crop_h, crop_y + delta_move)
            elif key == 81:  # Flèche gauche
                crop_x = max(0, crop_x - delta_move)
            elif key == 83:  # Flèche droite
                crop_x = min(w - crop_w, crop_x + delta_move)
            
        cv2.destroyAllWindows()

if __name__ == "__main__":
    crop_images()