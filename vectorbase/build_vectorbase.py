from neo4j import GraphDatabase
from py2neo import Graph, Node, Relationship
import os
import sqlite3
import xml.etree.ElementTree as ET
from langchain.embeddings import HuggingFaceEmbeddings
from chromadb.api.types import (
    Documents,
    EmbeddingFunction,
    Embeddings)
from langchain_community.vectorstores import Chroma
from vars_connexion import model_kwargs, encode_kwargs, model
from typing import List, Tuple

"""
Pipline permettant de vectoriser tous les XML de la base LEGI et de les mettre dans le vectorstore Chroma

"""



def parse_xml(file_path : str, element : str) -> str :
    """
    fonction pour récupérer le contenu textuel un XML sachant le chemin local vers celui-ci "file_path" 
    et la borne "element" dont il faut récupérer le contenu 
    """
    # Charger et parser le fichier XML
    tree = ET.parse(file_path)
    root = tree.getroot()
    # Trouver toutes les balises BLOC_TEXTUEL et extraire leur contenu
    bloc_textuel_contents = []
    elements = root.findall(element)
    if elements :
        for bloc_textuel in elements :
            text_content = ET.tostring(bloc_textuel, encoding='unicode', method='text')
            bloc_textuel_contents.append(text_content.strip())
    else : 
        bloc_textuel_contents.append("no data")

    
    return bloc_textuel_contents


def parse(file_path : str) -> str :
    """
  Fonction qui utilise "parse_xml" pour les bornes et ".//TITRE_TXT" et ".//BLOC_TEXTUEL/CONTENU" et qui rajoute la référence de l'article dans le texte de sortie
    """
  
    if file_path:
        titre0 = parse_xml(file_path, ".//TITRE_TXT")[0]
        article0 = f'Article {str(parse_xml(file_path, ".//NUM")[0])}'
        contenu0 = parse_xml(file_path, ".//BLOC_TEXTUEL/CONTENU")[0]
        if contenu0 != "no data":
            texte = "///////" + str(titre0) + " " + str(article0) +  " : " + "\n\n" + str(contenu0)

            return texte


def embedding_fonction(model_kwargs, encode_kwargs, model):
    """
    Génère la fonction d'embedding utilisée lors du peuplement du vectorstore
    """
    embeddings_croissant = HuggingFaceEmbeddings(
    model_name=model,     
    model_kwargs=model_kwargs, 
    encode_kwargs=encode_kwargs )

    return embeddings_croissant



def recherche_tous_les_chemins(adresse_BDD : str) -> List[str]:
    """
    retourne la liste de tous les chemins des XML du dossier à "adresse_BDD"
    """
    conn = sqlite3.connect(adresse_BDD)
    cursor = conn.cursor()

    query = """
    SELECT path
    FROM REFS
    """
    cursor.execute(query)
    result = cursor.fetchall() #retourne tout sous forme de liste de tuples
    conn.close()

    # Transforme la liste de tuples en une liste simple si nécessaire
    paths = [row[0] for row in result]

    return paths



def pipeline_build_vectorbase(adresse_BDD, model_kwargs, encode_kwargs, model, adresse_vectorstore):
    """
    Pipeline :
    1) on récupère les paths de tous les XML
    2) on récupère leur contenu textuel
    3) on vectorise chaque article
    """
    liste_liens = recherche_tous_les_chemins(adresse_BDD)
    embeddings_croissant = embedding_fonction(model_kwargs, encode_kwargs, model)
    
    # Initialiser la base de données une seule fois avant la boucle
    db = Chroma(persist_directory=adresse_vectorstore, embedding_function=embeddings_croissant)
    
    for file in liste_liens:
        if isinstance(file, str):
            texte = parse(file)
            if texte:
                db.add_texts([texte])
                print(texte)  
                db.persist()
    return db

    


