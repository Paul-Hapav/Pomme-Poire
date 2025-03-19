# Premier codes pour découvrir la génération de neurones sur Python

# Import des librairies

from kaggle_datasets import KaggleDatasets
import os

# Constantes 

# Fonctions/Procedures

def kaggle_setup(lib=2):
    # Procédure qui va récupérer le lien du dataset kaggle pour ce projet. 
    if lib == 1:
        path_lib = KaggleDatasets().get("moltean/fruits")
    else
        path_lib = KaggleDatasets().get("ishandandekar/fruitimagedataset")
    print(f"Adresse du dataset choisi: {path}")

    return path_lib

def path_to(lib=2,source=1):
    path=kaggle_setup(lib)
    match lib
    case 1:
        if source ==1:
            path = path+"/fruits-360_100x100/fruits360/Test"
        else 
            path = path+"/fruits-360_100x100/fruits360/Train"
    case _:
        if source == 1:
            path = path + "/test/test"
        else:
            path= path + "/train/train"
    
    assert os.path.exists(path),f"Le chemin trouve sur Kaggle est indisponible : {path}"

    apple_rep=[]
    pear_rep=[]
    exclusions=["Apple Core 1","Apple Rotten 1","Apple hit 1","Pear Stone 1"]

    for dir in os.listdir(path):
        if os.path.isdir(os.path.join(path,dir)):

            if dir.startswith("Apple") and dir not in exclusions :
                apple_rep.append(f"/{dir}")

            elif dir.startswith("Pear") and dir not in exclusions :
                pear_rep.append(f"/{dir}")

    with open("rep_apple.txt","w",encoding="utf-8") as apple_file:
        apple_file.write("\n".join(os.path.join(path, rep) for rep in apple_rep)))

    with open("rep_pear.txt","w",encoding="utf-8") as pear_file:
        pear_file.write("\n".join(os.path.join(path, rep) for rep in pear_rep)))

    return path


# Programme principal
# Test de la création des .txt et de l'ananlyse du dataset
if __name__=="__main__":
    print(f"Debut du programme")
    choix_dataset = int(input("Valeur du dataset : 1 Fruit 360 | autre : Autre dataset"))
    train_or_test = int(input("Valeur du jeu : 1= test | autre = train"))
    print(f"Fin du Test du programme. Le chemin utilisé est : {path_to(choix_dataset,train_or_test)}")