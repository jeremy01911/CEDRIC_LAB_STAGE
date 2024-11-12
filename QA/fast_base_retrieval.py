import os
import sqlite3
from typing import List, Tuple
from vars_connexion import BDD, chemin_LEGI

directory = chemin_LEGI  #modifier chemin_LEGI de vars_connexion si on veut en créer une nouvelle BDD
adresse_BDD = BDD 

"""
Scripts permettant d'interagir avec la base de données relationnelle

- create_fast_base : creation de la BDD à l'adresse voulue (modifier vars_connexion)
- query_fast_base : permet d'obtenir le path du XML dont on connait l'ID

"""


def create_BDD_refs (adresse : str) -> None:

   """
   On crée une table 
   """
   conn = sqlite3.connect(adresse)

   cursor = conn.cursor()
   cursor.execute( '''
   CREATE TABLE REFS (
               name INTEGER PRIMERY KEY,
               path INTEGER
               
   )
      ''' )
   
   conn.commit()
   conn.close()
   


def add_BDD_textes(adresse : str, liste : str) -> None:

   """
   On peuple la BDD avec des paires de (nom d'article, contenu de l'article)
   """

   conn = sqlite3.connect(adresse)
   cursor = conn.cursor()

   cursor.executemany( ''' insert into REFS (name, path)  VALUES (?, ?) ''', liste)

   conn.commit()
   conn.close()



def link_name_path(directory : str) -> List[tuple[str, str]]:
    """
    on parcoure tous les dossiers depuis directory et retourne une liste de  tuples  : (ID, file_path)
    """
    liste_tuples = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            if file_path.endswith('.xml'):
                split = file_path.split('/')
                last = split[-1].replace('.xml', '')
                tuple = (last, file_path)
                liste_tuples.append(tuple)
    return liste_tuples
        



def recherche_path(ID : str, bdd_texts : str) -> List[tuple[str]]:
    """
    retourne une liste de tuples avec un seul element : le path de  l'article recherché.
    renvoi une liste vide si il ne trouve pas
    """
    conn = sqlite3.connect(bdd_texts)
    cursor = conn.cursor()

    query = """
    select path
    FROM REFS
    WHERE name = ?
    """
    cursor.execute(query, (ID,))
    result = cursor.fetchone() 
    conn.close()

    return result


def create_fast_base(directory : str, adresse_BDD : str) -> None :
    """
    Fonction permettant de créer la base de données
    - creation de la base à une adresse donnée
    - ajout dans la base des tuples (ID, file_path)
    """
    create_BDD_refs (adresse_BDD)
    liste_tuples = link_name_path(directory)
    add_BDD_textes(adresse_BDD, liste_tuples)


def query_fast_base(adresse_BDD : str, ID : str) -> str:
    """
    Fonction permettant de faire une requête dans la base de données
    - retourne le chemin local vers le XML sachant son ID
    """
    
    if recherche_path(ID, adresse_BDD):
        lien = recherche_path(ID, adresse_BDD)[0]
        return lien
    else :
        return ""


if __name__ == "__main__":
    
    #create_fast_base(directory, adresse_BDD) #on crée la base de données
    lien = query_fast_base(adresse_BDD, 'LEGIARTI000006') #on fait une requête à la base de données
    print(lien)


    #il y a 1 320 186 XML dans le dossier

