import re
from langchain_openai import ChatOpenAI
from langchain_community.llms import Ollama
from langchain.schema import HumanMessage
import difflib
from typing import List, Tuple
from vars_connexion  import MODEL, MODEL_NAME, API_KEY

"""
Extraction des références standardisées à partir d'une question relationnelle

"""

"//////////////////////////////////// connexion aux BDD et API"


LLM = ChatOpenAI(model_name=MODEL_NAME, temperature=0, openai_api_key= API_KEY )
llm = Ollama(model = MODEL)


"//////////////////////////////////// connexion aux BDD et API"




def LLM_return_refs(question : str ) -> str :
    """"

    Utilisation d'un LLM pour identifier dans une question une référence à un article.
    Le LLM retourne un texte avec une référence par ligne telle que : 
    numero de l'article + nom du docuement

    arg : question (str)
    return : réferences (str)


    """
    message_content = (f""" voici une question : 
                       Début de la question /// 
                       
                       {question} 

                       /// fin de la question 

                N'essaye pas de répondre à la question
                N'essaye pas de répondre à la question

               Cette question fait référence à un ou plusieurs articles du droit Français.
               Retourne moi les références en sautant une ligne à chaque fois et en respectant ce formalisme : 
               
               numero de l'article + nom du docuement
               numero de l'article + nom du docuement
               numero de l'article + nom du docuement

               exemple :

                article 8 loi 2027934
                article 154 code des communes
                article 780-12 décret 2345
                article L234 arrêté 16 décembre 2013
                article 1 code de la propriété intellectuelle
                article RO-17 décret 4890-8
                article 90 amendement 3409
                article L12-23-45 ammendement 193434
                article 5 décret 363909

                ...

                N'essaye pas de répondre à la question contente toi de retourner les références qui apparaissent dans la question (ça ne demande de connaissances en droit)
               

    """)

    message = HumanMessage(content=message_content)

    reponse = LLM([message])
    texte = reponse.content
    return texte


def extract_num_article(texte : str) -> str:
    """
    Exemple de regex pour trouver les références d'articles avec différents formats.

    ex : 
    article 12
    article 123-8
    article 123-95-3
    article L.123-8
    article RO.123-8
    article L-123-8
    """
    
    pattern = r'article\s*[A-Za-z]{0,3}[.-_ ]?\d{1,5}(?:-\d{1,4})?'
    matches = re.findall(pattern, texte, re.IGNORECASE)
    return matches

def retirer_chiffres_et_occurrences(titre : str) -> str:
    """
    On nettoie le titre de l'article (courant ou référence) pour éviter le bruit et pouvoir identifier si c'est une loi, un article, un amendement, un code ect

    return : (str)
    """
    # Listes des motifs à supprimer
    motifs_a_supprimer = ['art.', 'janvier', 'février', 'mars', 'avril', 'mai', 'juin', 
                          'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre', 'article', 'l-', 'l.', 'r-', 'r.', 'R-', 'R.', 'L-', 'L.', 'l-' ]
    
    # Suppression des motifs spécifiques et des noms de mois
    for motif in motifs_a_supprimer:
       titre = titre.replace(motif, '')
    
    # Expression régulière pour les chiffres
    titre_clean = re.sub(r'\d+', '', titre)
    #print(chaine_sans_chiffres)
    
    return titre_clean.lower()


def get_type_document(titre_clean : str, orthographes: List[str]) -> str :
        """
        on remplace le titre de nettoyé par le type de document qu'il représente (loi, amendement, code ect...)
        return (str)
        """
        return difflib.get_close_matches(titre_clean, orthographes, n=1, cutoff=0.0)[0]

orthographes_correctes = ["code de l'action sociale et des familles", "code de l'artisanat", 'code des assurances', "code de l'aviation civile", "code du cinéma et de l'image animée", 'code civil', 'code de la commande publique', 'code de commerce', 'code des communes', 'code des communes de la nouvelle-calédonie', 'code de la consommation', "code de la construction et de l'habitation", 'code de la défense', 'code de déontologie des architectes', 'code disciplinaire et pénal de la marine marchande', "code du domaine de l'etat", "code du domaine de l'etat et des collectivités publiques applicable à la collectivité territoriale de mayotte", 'code du domaine public fluvial et de la navigation intérieure', 'code des douanes', 'code des douanes de mayotte', "code de l'éducation", 'code électoral', "code de l'énergie", "code de l'entrée et du séjour des étrangers et du droit d'asile", "code de l'environnement", "code de l'expropriation pour cause d'utilité publique", "code de la famille et de l'aide sociale", 'code forestier', 'code général de la fonction publique', 'code général de la propriété des personnes publiques', 'code général des collectivités territoriales', 'code général des impôts', 'code des impositions sur les biens et services', 'code des instruments monétaires et des médailles', 'code des juridictions financières', 'code de justice administrative', 'code de justice militaire', 'code de la justice pénale des mineurs', "code de la légion d'honneur de la médaille militaire et de l'ordre national du mérite", 'livre des procédures fiscales', 'code minier', 'code monétaire et financier', 'code de la mutualité', "code de l'organisation judiciaire", 'code du patrimoine', 'code pénal', 'code pénitentiaire', 'code des pensions civiles et militaires de retraite', 'code des pensions de retraite des marins français du commerce de pêche ou de plaisance', "code des pensions militaires d'invalidité et des victimes de guerre", 'code des ports maritimes', 'code des postes et des communications électroniques', 'code de procédure civile', 'code de procédure pénale', "code des procédures civiles d'exécution", 'code de la propriété intellectuelle', 'code de la recherche', "code des relations entre le public et l'administration", 'code de la route', 'code rural', 'code rural et de la pêche maritime', 'code de la santé publique', 'code de la sécurité intérieure', 'code de la sécurité sociale', 'code du service national', 'code du sport', 'code du tourisme', 'code des transports', 'code du travail', 'code du travail maritime', "code de l'urbanisme", 'code de la voirie routière', "décret", "arrêté", "amendement"]


def extract_chiffre__loi_ordonnance_decret(ref : str, type : str) -> str :
    """
    Extrait le numero de la loi, de l'ordonnace ou du décret à partir de la référence donnée par le LLM
    """
    parties = ref.split(type, 1)
    if len(parties)>1:
        chiffre = re.sub(r'\W|\s', '', str(re.findall(r'\d+', re.sub(r'[^\w\s]', '', str(parties[1])) )))
    else :
        chiffre = ""
    return chiffre


def return_references_formatées(texte : str) -> str :
    """
    Récupère toutes les références écrites par le LLM ligne par ligne, 
    extrait : type de document, numero de l'article, chiffre du document si necessaire, et reconstruit la référence
    retourne la liste des références standardisées
    """
    liste = texte.splitlines()
    liste_references = []
    for ref in liste:
        num_article = extract_num_article(ref)[0] if extract_num_article(ref) else "" 
        type = get_type_document(retirer_chiffres_et_occurrences(ref), orthographes_correctes)
        
        if type in {"décret", "loi", "ordonnance"}:
            chiffre = extract_chiffre__loi_ordonnance_decret(ref, type)
            reference = (num_article + " " + type + " "  + chiffre).strip()
            liste_references.append(reference)

        elif type == "arrêté":
            parties = ref.split("arrêté", 1)
            if len(parties)>1:
                pattern = r'\b\d{1,2} [a-zA-ZéèêëàâäôöùûüçÉÈÊËÀÂÄÔÖÙÛÜÇ]{1,12} \d{4}\b'
                matches = re.findall(pattern, texte)
            reference = (num_article + " " + type + " " + matches[0]).strip()  if matches else " "
            liste_references.append(reference)
        
        else : #pour les codes 
           reference = (num_article + " " + type).strip()
           liste_references.append(reference)
    
    return liste_references



def pipeline_references(question : str) -> str :
    """
    prend en entrée la question utilisateur et retourne la liste des references dans la question
    retourne toujours une str même quand il ne trouve rien

    arg : question (str)
    return : liste de references (list)

    """
    texte = LLM_return_refs(question)
    liste_references = return_references_formatées(texte)

    return liste_references
    
if __name__ == "__main__":

    result = pipeline_references("Que dit l'article ABC du code civil ?")
    print(result)

