import os
import unidecode
import glob
from random import randint
from os import removedirs
import random as rand
from bs4 import BeautifulSoup
from os import walk
import re
import os
import codecs
import pandas as pd
import difflib
import rdflib
from rdflib import URIRef, Literal
from py2neo import Graph, Node, Relationship
from rdflib.namespace import CSVW, DC, DCAT, DCTERMS, DOAP, FOAF, ODRL2, ORG, OWL, \
                               PROF, PROV, RDF, RDFS, SDO, SH, SKOS, SOSA, SSN, TIME, \
                               VOID, XMLNS, XSD

from vars_connexion import NEO4J_URL, NEO4J_AUTH


from graph.build_graph import adding_in_graph
from graph.build_graph import parser_or_not

from typing import List, Tuple

"""
Parsing des fichiers XML, extraction des references avec "pipeline" et ajout au graph NEO4J des articles via la fonction "adding_in_graph"
"""

"//////////////////////////////////// connexion aux BDD et API"

graph = Graph(NEO4J_URL, auth=NEO4J_AUTH)

"//////////////////////////////////// connexion aux BDD et API"



def count_key(key,data):
      c=0
      for k in data.keys():
        if k==key:
          c+=1
      return c

def checkKey(dict, key):
        if key in dict.keys():
            return True
        else:
            return False


def code_name(node):
        with codecs.open(node, 'r', 'UTF-8') as f:
            data = f.read()
            bs_data = BeautifulSoup(data, 'xml')
            child = bs_data.find('TITRE_TXT')
            if child != None:
                return child.text
def type_from_path(path):
    t = ''
    ID = ''
    if len(path) > 24:
        p = re.findall(r'[A-Z]+[0-9]+',path)
        if p != []:
            ID = p[-1][4:8]
    else:
        ID = path[4:8]
    if ID == "ARTI":
        t = "Article"
    if ID == "SCTA":
        t = "Section"
    if ID == "TEXT":
        t = "TEXT"
    if ID != 'TEXT' and ID != 'ARTI' and ID != 'SCTA':
        t = 'Not Defined'
    return t
def file_to_url(my_string):
    #
    url=''
    strr = my_string[8:]
    prefix=my_string[0:4]+'/'+my_string[4:8]+'/'
    my_list = [strr[idx:idx + 2] for idx in range(0, len(strr)+1, 2)]
    urls=[]
    for x in my_list:
            if x != my_list[-1]:
                 new=x+'/'
                 urls.append(new)
            else:
                if x == my_list[-1]:
                    urls.append(x)
    path=''.join(urls)
    path=prefix+path
    return path

def couper_apres_legitex(string):
    # Utiliser une expression régulière pour trouver "legitex" suivi de 12 chiffres
    match = re.search(r'(LEGITEXT\d{12})', string)
    
    if match:
        # Récupérer la position de fin de la première correspondance
        end_pos = match.end()
        # Couper la chaîne juste après la première correspondance
        return string[:end_pos]
    else:
        # Si aucune correspondance n'est trouvée, retourner la chaîne originale
        return string
    
#=====================================PARSER========================================

def parser (TAGS,lk,file):
      res={}
      with codecs.open(file, 'r', 'UTF-8') as f:
          data = f.read()
      bs_data = BeautifulSoup(data, 'xml')
      prefix='file/'
      for t in TAGS:
        if t=='NOTA':
            child = bs_data.find(t)
            ss=child.text

            res['denoted']=ss
        else:
            if t=='BLOC_TEXTUEL':
                child = bs_data.find(t)
                res['txt']=child.text
            else:
                    child=bs_data.find (t)
                    res[t]= unidecode.unidecode(child.text)
      res['nxv']=[]
      if type_from_path(file) == 'Article':
          res['is_part_of'] = []
          res['LIENS_cible']=[]
          res['LIENS_cible_in'] = []
          res['LIENS_source']=[]
          res['LIENS_source_of'] = []
          for t in lk:
                  if t == 'CONTEXTE':
                      child = bs_data.find(t)

                      if child != None:
                          chil = child.findChildren()
                          for c in chil:
                              cc = c.attrs
                              if 'id' in cc.keys():
                                  res['is_part_of'].append(cc['id'])
                  if t == "LIEN_ART":
                      child = bs_data.findAll(t)
                      for c in child:

                          if c.attrs['id']!=file[78:98]:
                             res['nxv'].append(c.attrs['id'])
                  if t=='LIENS':
                      child=bs_data.find(t)
                      childs=child.findChildren()
                      for c in childs:
                          if c.attrs['sens']=='cible':
                              t=c.attrs['typelien'].capitalize()
                              if t=='Modifie':
                                  t='Modification'
                              else:
                                  if t=='Abroge':
                                      t='Abrogation'
                              res['LIENS_cible'].append((file.replace(prefix,''),t,c.attrs['id'],c.attrs['datesignatexte'],c.text))
                              #res['LIENS_cible_in'].append((file.replace(prefix,''),c.attrs['typelien'].capitalize(),c.text))
                          elif c.attrs['sens']=='source':
                              res['LIENS_source'].append((file.replace(prefix,''),c.attrs['typelien'].capitalize(),c.attrs['id'],c.attrs['datesignatexte'],c.text))
                              #res['LIENS_source_of'].append((file,c.attrs['typelien'].capitalize(),c.text))
                              #print(file+' '+c.attrs['typelien'].capitalize()+' in '+c.text)

          res['is_article_of']=Literal(code_name(file),datatype=XSD.string)
          res['title']='Article '+res['NUM']+' du '+code_name(file)

      else:

          if type_from_path(file)=='Section':
              res['has_part'] = []
              res['is_part_of'] = []
              for t in lk:
                  if t=='STRUCTURE_TA':
                      child = bs_data.find(t)

                      if child != None:
                          chil = child.findChildren()
                          for c in chil:
                            p=c.attrs
                            res['has_part'].append(p['id'])
                  else:
                      if t=='CONTEXTE':
                          child = bs_data.find(t)
                          if child != None:
                              chil = child.findChildren()
                              for c in chil:
                                  cc=c.attrs
                                  if 'id_txt'in cc.keys():
                                    res['is_part_of'].append(cc['id_txt'])

      #print(res)
      return res


def parser_TEXT(file):

    if type_from_path(file) == 'TEXT':
        res={}
        with codecs.open(file, 'r', 'UTF-8') as f:
            data = f.read()
        bs_data = BeautifulSoup(data, 'xml')
        Link_tags = ['STRUCT','VERSION_A_VENIR']
        TAGS = ['ID', 'DATE_PUBLI', 'DATE_TEXTE', 'DERNIERE_MODIFICATION', 'NUM', 'NOR']
        l = []
        keys = []
        for t in TAGS:
            child = bs_data.find(t)

            res[t] = child.text

        res['title'] = []
        res['has_part'] = []
        res['VERSIONS_A_VENIR'] = []
        for tt in Link_tags:
            if tt == 'STRUCT':
                child = bs_data.find(tt)
                if child != None:

                    chil = child.findChildren()
                    for c in chil:
                        params = c.attrs
                        res['title'].append(unidecode.unidecode(c.text))
                        res['has_part'].append(params['id'])
                        file_cut = couper_apres_legitex(file)
                        print(file_cut)
                        print(file_cut + '/section_ta/' + params['url'])
                        res['NameCode'] = unidecode.unidecode(
                            str(code_name(file_cut + '/section_ta/' + params['url'])))
            else:
                child = bs_data.find(tt)
                res['VERSIONS_A_VENIR'].append((child.text or '').replace('\n', ''))
        #print(res)
        return res
    

def Parser_SCTA(file):
    # print('parsing section', file)
    if type_from_path(file) == "Section":
        lk = ['STRUCTURE_TA', 'CONTEXTE', 'TITRE_TM']
        TAGS = ['ID', 'TITRE_TA']
        res = parser(TAGS, lk, file)
        return res
    # parser(TAGS,lk,file)
    else:
        print("Wrong Document Type")





def Parser_arti(file):
    # print(bs_data)
    if type_from_path(file) == "Article":
        lk = ['CONTEXTE', 'LIENS', 'LIEN_ART']
        TAGS = ['ID', 'NUM', 'NATURE', 'ETAT', 'DATE_DEBUT', 'DATE_FIN','NOTA','BLOC_TEXTUEL']
        res = parser(TAGS, lk, file)

        #print(res)

        return res
        
    
    else:
        print("Wrong Document Type")



def struct(file):
    #print(file)
    res = []

    with codecs.open(file, 'r', 'UTF-8') as f:
        data = f.read()

        bs_data = BeautifulSoup(data, 'xml')
        child = bs_data.find('STRUCTURE_TA')

        if child != None:
            chil = child.findChildren()
            for c in chil:
                params = c.attrs
                if 'url' in params.keys():
                    if checkKey(params, 'url') == True:
                        res.append(params["url"])
                else:
                    url=file_to_url(params['id'])
                    res.append(url)
        else:
            child = bs_data.find('STRUCT')
            if child != None:
                chil = child.findChildren()
                for c in chil:
                    params = c.attrs
                    if 'url' in params.keys():
                        if checkKey(params, 'url') == True:
                            res.append(params["url"])
                    else:
                        if 'url' not in params.keys() and 'id' in params.keys():
                         url = file_to_url(params['id'])
                         res.append(url)
        #print(res)
        return res

#on donne une structure en entrée (livre, titre, document ...) il va aller automatiquement chercher tous les liens vers les sous parties (document structure et texte)
#quand on arrive au niveau de l'artcle : retourne un dictionnaire
def rec_prs(file):
    #print(file)
    lst = struct(file)
    paths = list(lst)
    #print(paths)
    #prefix = find_start('/Users/jeremytournellec/Desktop/CodifiedTextParser/file/document')
    for dd in paths:
        t=dd.replace('/','')
        #print(t)
        file_cut = couper_apres_legitex(file)

        if type_from_path(t) == "Section":
            prefix = file_cut + '/section_ta'
            path = prefix + dd
            Parser_SCTA(path)
            # print(dd,'  ',type_from_path(to_type))
            rec_prs(path)
        else:
            if type_from_path(t)=='Article':
                    prefix = file_cut + '/article/'
                    #print(prefix)
                    rl=dd[0:len(dd)-3]
                    #print(rl)
                    path = prefix + rl+'/'+ t+'.xml'
                    #print(t)
                    if parser_or_not(graph, t) == 'NO':
                        ID, name, refs_cible, refs_source, ETAT = pipeline(path) #extraction des références
                        if ETAT in ('VIGUEUR', 'VIGUEUR_DIFF', 'ABROGE', 'ABROGE_DIFF', 'ANNULE') :
                            adding_in_graph(ID, name, refs_cible, refs_source) #ajout au graph
                            print(ID)
                   


#file/document/05/62/78/LEGITEXT000005627819/section_ta/LEGI/SCTA/00/00/06/13/29/LEGISCTA000006132961.xml

#================USEFULL=====================================================================================

def read_file(file):
        data=''
        f = codecs.open(file, 'r', 'UTF-8')
        for line in f:
            data+=line
        return data
            


listeFichiers = []
res=[]

#trouve tous les repertoires qui ont un nom tel que : LEGITEXT000005627819 (donc tous les repertoires de fichiers)
def find_start(start):
        for (repertoire, sousRepertoires, fichiers) in walk(start):
         listeFichiers.extend(sousRepertoires)
        for e in listeFichiers:
            if re.match('[A-Z]+[0-9]+',e):


                    for dirpath, dirnames, filenames in os.walk(start):
                        for dirn in dirnames:
                            if dirn == e:
                                filename = os.path.join(dirpath, dirn)
                                filename = filename.replace("\\", "/")

                                res.append(filename)
        return res

    #print(find_start('file/document'))

#supprime les doublons dans la liste de fichiers txt
def unique(l):
        uniq=[]
        for x in l:
            if x not in uniq:
                uniq.append(x)
        return uniq

#retourne le premier XML du dossier (chemin le plus cours depuis le point de départ) => fonction qui était utile à start_all pour peupler le graph avec les textes
#est ce que c'est lui qui a les refernces originelles de l'arboressence ?
def frst_file(path):
        res=[]
        for pth in path:
            filepath = glob.glob(pth+'/texte/struct/*.xml', recursive=True)
            if filepath:
                res.append(filepath[0])
                res=unique(res)
        return res

def start_all(files):
   for file in files:
                #parser_TEXT(file)
                rec_prs(file)



#================EXTRACTION ET FORMATTAGE DES REFERENCES DE L'ARTICLE COURANT=====================================================================================
"""
Les fonctions extract permettent d'extraire avec des REGEX les references aux articles. 

Chaque article a des listes de tuples représentant les references entrantes et sortantes. Les tuples contiennent un ID (str), le type de relation (str) et le nom de l'article référent.
Le nom de l'article référent n'est pas toujours naturel et il serait difficile à trouver dans une BDD donc on le standardise : numero d'article + article + nom du document + numero du document (str)

on distingue plusieurs fonctions:

- extract_num_article : extrait le numero d'article  de l'article courant
- extract_numref_article : extrait le numero des articles références
- extract_document : on extrait le numero du document ou la date si c'est un décret
- clean : permet de nettoyer le titre de l'article pour pouvoir appliquer find_titre_document plus efficacement
- find_type_document : compare le titre de l'article courant avec les noms des differents types de documents légaux pour savoir à quel document il correspond.
On conserve le document qui a la plus longue str en commun. On utilise en amont clean  pour éviter le parasitage.
- construct_ref : met bout à bout la référence de l'article, le type de document légal et son numero associé

- pipeline : mise bout à bout : on extrait les références des articles, textes juridiques et numeros et on les reconstruit de manière uniforme pour les articles courants et leurs références.
"""

def extract_num_article(texte : str) -> str :
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
    
    return str(matches[0]) if matches else ''


def find_type_document(chaine : str, orthographes : str) -> str:
        """
        on remplace le titre de l'article par le type qu'il représente (loi, amendement, code ect...)
        return (str)
        """
        return difflib.get_close_matches(chaine, orthographes, n=1, cutoff=0.0)[0]

orthographes_correctes = ["code de l'action sociale et des familles", "code de l'artisanat", 'code des assurances', "code de l'aviation civile", "code du cinéma et de l'image animée", 'code civil', 'code de la commande publique', 'code de commerce', 'code des communes', 'code des communes de la nouvelle-calédonie', 'code de la consommation', "code de la construction et de l'habitation", 'code de la défense', 'code de déontologie des architectes', 'code disciplinaire et pénal de la marine marchande', "code du domaine de l'etat", "code du domaine de l'etat et des collectivités publiques applicable à la collectivité territoriale de mayotte", 'code du domaine public fluvial et de la navigation intérieure', 'code des douanes', 'code des douanes de mayotte', "code de l'éducation", 'code électoral', "code de l'énergie", "code de l'entrée et du séjour des étrangers et du droit d'asile", "code de l'environnement", "code de l'expropriation pour cause d'utilité publique", "code de la famille et de l'aide sociale", 'code forestier', 'code général de la fonction publique', 'code général de la propriété des personnes publiques', 'code général des collectivités territoriales', 'code général des impôts', 'code des impositions sur les biens et services', 'code des instruments monétaires et des médailles', 'code des juridictions financières', 'code de justice administrative', 'code de justice militaire', 'code de la justice pénale des mineurs', "code de la légion d'honneur de la médaille militaire et de l'ordre national du mérite", 'livre des procédures fiscales', 'code minier', 'code monétaire et financier', 'code de la mutualité', "code de l'organisation judiciaire", 'code du patrimoine', 'code pénal', 'code pénitentiaire', 'code des pensions civiles et militaires de retraite', 'code des pensions de retraite des marins français du commerce de pêche ou de plaisance', "code des pensions militaires d'invalidité et des victimes de guerre", 'code des ports maritimes', 'code des postes et des communications électroniques', 'code de procédure civile', 'code de procédure pénale', "code des procédures civiles d'exécution", 'code de la propriété intellectuelle', 'code de la recherche', "code des relations entre le public et l'administration", 'code de la route', 'code rural', 'code rural et de la pêche maritime', 'code de la santé publique', 'code de la sécurité intérieure', 'code de la sécurité sociale', 'code du service national', 'code du sport', 'code du tourisme', 'code des transports', 'code du travail', 'code du travail maritime', "code de l'urbanisme", 'code de la voirie routière', "décret", "arrêté", "amendement"]


def extract_numref_article (texte : str) -> str :
    """
    Exemple de regex pour trouver les références d'articles
    ex : 
    art. 12
    art. 123-8
    art. 123-95-3
    return : (str) : article 113-456, article  79 ect ...
    """
    
    pattern = r'art\.?\s*?[A-Za-z]{0,3}\.?\s*\d{1,5}(?:-\d{1,4}\*?)?(?:-\d{1,4}\*?)?|[A-Za-z]+\*\d{1,5}(?:-\d{1,4})?(?:-\d{1,4})?'

    matches  = re.findall(pattern, texte)
    
    return 'article' + ' ' +(re.sub(r'[.*]', '', matches[0]).replace("art", "")).strip() if matches else  ''
    

def extract_ref_document(type : str, texte : str) -> str:
    """
    Exemple de regex pour trouver les références de type n°2007-1850
    ex :
    n°2007
    n°2007-1850
    n°1
    n°12345-678-91011
    """
    if type == 'loi' or type == 'décret' or type == 'amendement':
        pattern = r'n°\d{1,15}(?:-\d{1,15})*'
        matches = re.findall(pattern, texte)
        chiffre = re.sub(r'\W|\s', '', str(re.findall(r'\d+', re.sub(r'[^\w\s]', '', str(matches)) )))
        ref_document = type + " " + chiffre    
    
    elif type == 'arrêté':
        pattern = r'\b\d{1,2} [a-zA-ZéèêëàâäôöùûüçÉÈÊËÀÂÄÔÖÙÛÜÇ]{1,12} \d{4}\b'
        matches = re.findall(pattern, texte)
        ref_document = type + " " + matches[0]  if matches else " "
        
    else :
        ref_document = type

    return ref_document



def clean(chaine : str) -> str:
    """
    On nettoie le titre de l'article (courant ou référence) pour éviter le bruit et pouvoir identifier si c'est une loi, un article, un amendement, un code ect
    """
    motifs_a_supprimer = ['art.', 'janvier', 'février', 'mars', 'avril', 'mai', 'juin', 
                          'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre']
    
    for motif in motifs_a_supprimer:
        chaine = chaine.replace(motif, '')
    
    chaine_sans_chiffres = re.sub(r'\d+', '', chaine)
    
    return chaine_sans_chiffres.lower()


def construction_ref(type : str, numero_article : str, titre : str) -> str:
    """
    construction de la reference standardisée : numero_article + nom_document
    ex :
    article 12-34 code des procédures civiles d'execution
    article 137-8 loi 45690
    """
    
    ref_document = extract_ref_document(type, titre)
    ref = str(numero_article).strip().lower() + " " + str(ref_document).strip().lower()
    return ref



def pipeline(adresse : str) -> Tuple[str, str, List[Tuple[str, str, str]], List[Tuple[str, str, str]], str]:
    """"
    Parsing des articles, extraction des références cibles et sources, mise en forme des relations sous cette forme :
    numero d'article + nom du document
    retourne la référence de l'article courant, son ID, les listes des articles reliés (type de référence, ID, nom standardisé) et l'état juridique de l'article courant
    """

    #on extrait le numero de l'article courant, on extrait le type de document (code, loi...) on reconstruit la référence

    refs_source = []
    refs_cible = []
    
    res = Parser_arti(adresse)
    ETAT = res['ETAT']
    txt = res['txt'].lower().strip()
    ID = res['ID'].upper().strip()

    numero_article = str(extract_num_article(res['title']))
    type = find_type_document(clean(res['title']), orthographes_correctes) 
    ref_courante = construction_ref(type, numero_article, res['title']) 
   
    #TRAITEMENT DES REFERENCES
    #on extrait le numero de l'article de chaque référence entrante ou sortante, on reconstruit les références et on fait des listes de références entantes et sortantes

    for i in res['LIENS_source']:
        titre = i[4]
        numero_article = str(extract_numref_article(titre))
        titre_clean = clean(titre)
        type = find_type_document(titre_clean, orthographes_correctes)
        ref = construction_ref(type, numero_article, titre)
        refs_source.append([i[1].strip().lower(), i[2].strip().upper(), ref.strip().lower()]) #liste des articles "liens source". Chaque reference est représentée par une liste avec ID, type de référence, nom standardisé

    for i in res['LIENS_cible']:
        titre = i[4]
        numero_article = str(extract_numref_article(titre))
        titre_clean = clean(titre)
        type = find_type_document(titre_clean, orthographes_correctes)
        ref = construction_ref(type, numero_article, titre)
        ref.append([i[1].strip().lower(), i[2].strip().upper(), ref.strip().lower()]) #liste des articles "liens cibles". Chaque reference est représentée par une liste avec ID, type de référence nom standardisé

    return ID, ref_courante, refs_cible, refs_source, ETAT




