# Premier codes pour découvrir la génération de neurones sur Python

# Import des librairies

import kagglehub
import os

# Constantes 

# Fonctions/Procedures

def kaggle_setup():
    # Procédure qui va récupérer le lien du dataset kaggle pour ce projet. 
    path = kagglehub.dataset_download("ishandandekar/fruitimagedataset")
    print(f"Adresse du dataset general: {path}")

    return path

def fruit_path(source=1):
    path=kaggle_setup
    if source ==1:
        path=path+"/test/test"
    else:
        path=path+"train/train"
    
    assert os.path.exists(path),f"Le chemin trouve sur Kaggle est indisponible : {path}"

    apple_rep=[]
    pear_pre=[]
    for dir in os.listdir(path):
        if os.path.isdir(os.path.join(path,dir)):
            if dir.startswith("Apple"):
                apple_rep.append(f"/{dir}")
            elif dir.startswith("Pear"):
                pear_pre.append(f"/{dir}")
    with open("rep_apple.txt","w",encoding="utf-8") as apple_file:
        apple_file.write("\n".join(apple_rep))
    with open("rep_pear.txt","w",encoding="utf-8") as pear_file:
        pear_file.write("\n".join(pear_pre))


# Programme principal
# Test de la création des .txt et de l'ananlyse du dataset
if __name__=="__main__":
    print("Debut du programme")

# Download latest version
path = kagglehub.dataset_download("ishandandekar/fruitimagedataset")

print("Path to dataset files:", path)