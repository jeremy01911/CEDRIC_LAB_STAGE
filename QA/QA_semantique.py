from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_community.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI


from vars_connexion import model_kwargs, encode_kwargs, model


"""
Ce pipeline retourne une List[str] : le contenu de tous les articles retrouvé par cosine similarity 
entre l'embedding de la question et les embeddings dans le vectorstore

"""


def embedding_fonction(model_kwargs, encode_kwargs, model):
    """
    Génère la fonction d'embedding utilisée lors du peuplement du vectorstore
    """
    embeddings_croissant = HuggingFaceEmbeddings(
    model_name=model,     
    model_kwargs=model_kwargs, 
    encode_kwargs=encode_kwargs )

    return embeddings_croissant



def open_vectorstore(adresse_vectorstore: str):

    embedding = embedding_fonction(model_kwargs, encode_kwargs, model)
    db3 = Chroma(embedding_function=embedding, persist_directory=adresse_vectorstore)
    return db3



def pipeline_semantique(question : str, adresse_vectorstore : str, k):
    """
    Vectorise la "question" et returne les k meilleurs resultats par "similarity search" 
    """
    refs_semantiques = []
    db = open_vectorstore(adresse_vectorstore)
    search_results = db.similarity_search(query=question, k=k)
    for el in search_results:
        el2 = str(el).replace('page_content=', '')
        refs_semantiques.append(el2)
    return refs_semantiques
    #print(refs_semantiques)





#tests pour vérifier le fonctionnement du pipeline sémantique seul

if __name__ == "__main__":
    #question = "La loi française sur l'adoption stipule que l'adoption peut être ouverte à des couples mariés depuis plus de deux ans ou âgés de plus de 28 ans, ainsi qu'aux célibataires de plus de 28 ans. L'adoptant doit être au moins 15 ans plus âgé que l'adopté, sauf dans le cas de l'adoption de l'enfant du conjoint. Il existe deux types d'adoption : l'adoption plénière, qui rompt tout lien avec la famille biologique, et l'adoption simple, qui maintient certains liens. Les adoptants doivent obtenir un agrément délivré par le service de l'aide sociale à l'enfance."
    question = "Que dit le code civil sur l'adoption ?"
    question = "Selon la loi française, l'âge minimal pour adopter un enfant est de 28 ans. Cela s'applique aussi bien aux célibataires qu'aux couples mariés. De plus, pour les couples, ils doivent être mariés depuis au moins deux ans si l'un des conjoints a moins de 28 ans. Ces conditions visent à assurer une certaine maturité et stabilité chez les adoptants avant d'accueillir un enfant."
    #adresse_vectorstore = "/Users/jeremytournellec/Desktop/premiertest"
    adresse_vectorstore = "/Users/jeremytournellec/Desktop/testchroma"
    k = 3

    refs_semantiques = pipeline_semantique(question, adresse_vectorstore, k)
    print(refs_semantiques)

    

   