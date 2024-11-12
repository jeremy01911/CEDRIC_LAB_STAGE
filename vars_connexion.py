"""

Variables de connexion :

- connexion au graph database
- connexion aux différentes API (on peut choisir laquelle utiliser dans le main_answer)
- paramètres pour l'utilisation du modèle d'embedding
- adresses du vectorstore et de la BDD relationnelle : changer les adresse si on en crée de nouvelles avec fast_base_retrieval ou main_vectorstore
- adresse du dossier avec les XML de legi, changer l'adresse locale en fonction de la machine

"""


#Graph database Neo4j

NEO4J_URL = "**********"
NEO4J_AUTH = ("neo4j", "password")


#OpenAI

MODEL_NAME = "gpt-4"
API_KEY = "**********"

#Llama 3 8B local

MODEL = 'llama3'

#Llama 3 70B deepinfra

API_TOKEN = "************"
MODEL_ID = 'meta-llama/Llama-2-70b-chat-hf'



#paramètres embedding pour build_vectorbase


model_kwargs = {'device':'cpu'}
encode_kwargs = {'normalize_embeddings': False}
model = 'manu/sentence_croissant_alpha_v0.4'

#adresse vectorstore

vectorstore = "/Users/jeremytournellec/votre/adresse"


#adresse BDD

BDD = '/Users/votre/adresse'

#dossier XML 

chemin_LEGI = '/Users/votre/adresse'


