from py2neo import Graph, Node, Relationship
import xml.etree.ElementTree as ET
import os

from langchain.chains import LLMChain
from langchain_core.prompts import PromptTemplate

from QA.extract_refs_relationnel import pipeline_references

from langchain_community.llms import DeepInfra
from langchain_openai import ChatOpenAI

from vars_connexion import MODEL_ID, API_TOKEN, NEO4J_URL, NEO4J_AUTH
from QA.fast_base_retrieval import adresse_BDD
from QA.fast_base_retrieval import query_fast_base
from QA.extract_refs_relationnel import pipeline_references
from typing import List, Tuple

"""

Ce pipeline retourne une List[str] : le contenu de tous les articles dont il est fait référence dans une question relationnelle 
ainsi que les textes des articles qui sont en relation directe avec eux.

1) trouver dans le BDD graph l'ID des références
2) recherche des chemins des références connaissant leur ID dans la BDD relationnelle
3) parsing des XML dont on a récupéré le chemin, et récupération du contenu textuel

"""

"//////////////////////////////////// connexion aux BDD et API"


# Connexion à Neo4j
graph = Graph(NEO4J_URL, auth=NEO4J_AUTH)


"//////////////////////////////////// connexion aux BDD et API"



def retrieve_ID(NAME : str ) -> str:

    """"
   On récupère l'ID de l'article courant dans le BDDgraph à partir de sa référence normalisée.
   Fonction utilisée dans : retrieve_all_id
    arg : NAME nom standardisé de l'article courant (str)
    return : adresse relative exemple : LEGIARTI000006204294 (str)
    """


    result = graph.run("MATCH (a:Article {name: $NAME}) RETURN a.ID AS id", NAME= NAME.lower())
    ids = []
    if result :
        for record in result:
            ids.append(record["id"])
        if ids : #si il a trouvé des ID
            ID = ids[0]

        else :
            ID = ""

        return ID.upper()
    

def retrieve_all_id(NAME : str) -> List[str] :

    """
    On récupère l'ID des articles dont il fait référence dans la question ainsi que l'ID de leurs relations
    arg : name : nom standardisé de l'article courant (str) , refs_extraites : liste des noms standardisés des références de l'article courant (str)
    return : liste_refs, liste des IDs des références directes et leurs références (list)
    """
    liste_refs  = []
 
    liste_refs = []
    ID = retrieve_ID(NAME) #on récupère l'ID de la référence dans la question
    if ID :
        liste_refs.append(ID)
    
        related_nodes = graph.run("""
            MATCH (a:Article {ID: $ID})
            OPTIONAL MATCH (a)-[]-(neighbor)
            RETURN a, collect(neighbor.ID) AS neighborIDs
            """, ID=ID).data()

        if related_nodes:
            for record in related_nodes:
                if record is not None and 'neighborIDs' in record:
                    for neighbor_id in record['neighborIDs']:
                        liste_refs.append(neighbor_id)
    else : 
        liste_refs = []
    #print(liste_refs)
    return liste_refs
        

def parse_xml(file_path : str, element : str) -> str:
    """
    Récupère le contenu dans la borne voulue "element" dans le fichier XML dont on connait le chemin "file path"
    arg : file_path : un lien  local(str), element : la borne recherchée dans le XML (str)
    return : le contenu du tag XML voulu (str)
    """
    print(file_path)
    tree = ET.parse(file_path)
    root = tree.getroot()
    
    bloc_textuel_contents = []
    elements = root.findall(element)
    if elements :
        for bloc_textuel in elements :
            text_content = ET.tostring(bloc_textuel, encoding='unicode', method='text')
            bloc_textuel_contents.append(text_content.strip())
    else : 
        bloc_textuel_contents.append("no data")
        #print('lol')
    #print(bloc_textuel_contents)

    
    return bloc_textuel_contents

def extraire_relation(list : List, i : str , titrei : str, titre0 : str, article0 : str, articlei : str) -> str:

    """
    Rédige une phrase illustrant la relation entre deux articles pour que le LLM puisse l'utiliser en contexte
    arg : liste des références (list) titrei, titre0 article0 et articlei qui sont les titres et numero d'article de la référence 0 de la liste (mentionné dans la question) et de la référence i associée (str)
    return une phrase à chaque appel (pour chaque référence i) (str)
    """
    article_cité = list[0]
    article_recherche = list[i]
    liste_refs = []
    type = ''

    related_nodes = graph.run("""
        MATCH (a:Article {ID: $ID1})-[r]->(b:Article {ID: $ID2})
        RETURN type(r)
        """, ID2 = list[0], ID1 = list[1] )
    
    for record in related_nodes:
        liste_refs.append(record)

    if liste_refs:
        type = f' titre : {titrei} {articlei}  (relation :{liste_refs[0]} sur {titre0} {article0}) '
   
    else:
        related_nodes = graph.run("""
        MATCH (a:Article {ID: $ID1})-[r]->(b:Article {ID: $ID2})
        RETURN type(r)
        """, ID2 = list[i], ID1 = list[0])
    
        for record in related_nodes:

            liste_refs.append(record)
            if liste_refs:
                type = f'  {titrei} {articlei} (relation : {liste_refs[0]}  par {titre0} {article0})'
    return type



def parse(list : List) -> List[str] :
    """
    arg : liste des ID d'un article cité dans la question et de ses relations
    rédige le contexte qui sera fourni au LLM avec le nom des articles, le type de relation netre eux obtenu avec "extraire_relation" et leur contenu
    return : liste avec chaque élement étant le texte asocié à une référence (list)
    """
    all_texte = []

    print(list)
    for i, element in enumerate(list) : #list est une liste de ID.xml
        file_path = query_fast_base(adresse_BDD, element) #on récupère le path à partir de l'ID
        if file_path:
            titre = parse_xml(file_path, ".//TITRE_TXT")[0]
            article = f'Article {str(parse_xml(file_path, ".//NUM")[0])}'
            contenu = parse_xml(file_path, ".//BLOC_TEXTUEL/CONTENU")[0]

            if i == 0:
                titre0, article0, contenu0 = titre, article, contenu
                texte = f"///////{titre0} {article0} : \n\n{contenu0}"

            else:
                titrei, articlei, contenui = titre, article, contenu
                type_relation = extraire_relation(list, i, titrei, titre0, article0, articlei) 
                texte = f"///////// {type_relation}\n\n{contenu}"
            
            all_texte.append(texte) 
        
        elif i == 0:
            titre0, article0, contenu0 = "", "", ""
            all_texte.append("")
        else :
            all_texte.append("")

    return all_texte 




def return_toutes_refs(references_question : List[str]) -> List[str]: #liste des références mères (textuelles)
    """
    1) extraction des ID associés aux références textuelles
    2) recherche des relations associés à cet ID (liste d'ID)
    3) parsing de toutes les références et construction de phrases contextuelles pour le LLM (liste de texte)
    4) pour chaque référence mère ajout des listes avec les phrases contextuelles pour chaque reference associée
    """
    liste_refs_pour_LLM = []
    already_in = set()

    for reference in references_question:  #énumère sur la liste des références normalisées mères , ex: [article 12 code civil, article 13 loi 2340] 
        liste_references = retrieve_all_id(reference) #retourne la liste d'ID des références  1), 2)  

        if liste_references:
            new_list_references = [el for el in liste_references if el not in already_in]
            already_in.update(new_list_references)
            all_texte = parse(new_list_references) #fonction qui retrouve le lien de chaque article, récupère le titre et le contenu. (str) 3) 
            liste_refs_pour_LLM += all_texte #4) 

    return liste_refs_pour_LLM if liste_refs_pour_LLM else []



def filtre_pertinence_template(art : str, question : str):
    """
    template pour la  fonction permettant de ne conserver que les sources support les plus pertinentes
    """

    template = """Je dispose d'une base de données contenant plusieurs articles juridiques. J'ai une question spécifique à laquelle je cherche des réponses ou des éléments de réponse. Pour chaque article que je vais te fournir, je voudrais que tu détermines s'il est utile pour répondre à la question suivante :

Question : {question}

Pour chaque article, évalue les points suivants :

L'article traite-t-il directement ou indirectement du sujet de la question ?
L'article fournit-il des informations ou des arguments pertinents qui peuvent aider à répondre à la question ?
L'article cite-t-il des cas, lois ou précédents juridiques qui sont en lien avec la question posée ?
L'article est il cité dans la question ? 
L'article est il lié à l'article cité dans la question par la bonne relation exprimée dans la question (parmis les relation possibles : citation, codification, création, aborogation, annulation, déplacement) ?
Réponds par "Oui" ou "Non" pour chaque point 

Article : {art}
   
    """
    prompt = PromptTemplate.from_template(template)

    return prompt



def filtre_pertinence(llm, liste_refs_pour_LLM, question) -> List[str]:
    """
    fonction permettant de ne conserver que les sources support les plus pertinentes
    """
    liste_refs_pour_LLM_filtree = []
    for el in liste_refs_pour_LLM:
        prompt = filtre_pertinence_template(el, question)
        llm_chain = LLMChain(prompt=prompt, llm=llm)
        result = llm_chain.run(question=question, art=el)
        #print(result)
        if "OUI" or "oui" or "Oui" in result:
            liste_refs_pour_LLM_filtree.append(el)
    return liste_refs_pour_LLM_filtree



def pipeline_relationnel(question : str, llm : None) -> List[str]: 
    """
   Pipeline relationnel extrayant les relations de la quetion et retournant le texte support pour le LLM
    """
    references_question = pipeline_references(question) #extraction des références dans la question
    if references_question :
    
        liste_refs_pour_LLM = return_toutes_refs(references_question) 
        ##/// Filtrage //
        if 0 < len(liste_refs_pour_LLM) < 10:
            liste_refs_pour_LLM = filtre_pertinence(llm, liste_refs_pour_LLM, question)
    else :
        liste_refs_pour_LLM = []

    return liste_refs_pour_LLM

            
if __name__ == "__main__":

    result = parse (['JORFT68776'])
    print(result)
    #res = retrieve_ID('article 6-1 code civil')
    #print(res)