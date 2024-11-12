from QA.QA_relationnel import pipeline_relationnel
from QA.QA_semantique import pipeline_semantique
from langchain_core.prompts import PromptTemplate
from langchain_community.llms import DeepInfra
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain
from vars_connexion import MODEL_ID, API_TOKEN, vectorstore, MODEL_NAME, API_KEY

"""
les pipelines relationnels et sémantiques se rejoignent dans ce script

"""


"//////////////////////////////////// connexion aux BDD et API"

adresse_vectorstore = vectorstore


#llm = DeepInfra(model_id=MODEL_ID, deepinfra_api_token = API_TOKEN )
#llm.model_kwargs = {
    #"temperature": 0.7,
    #"repetition_penalty": 1.2,
   # "max_new_tokens": 250,
   # "top_p": 0.9,
#}

llm = ChatOpenAI(model_name=MODEL_NAME, temperature=0, openai_api_key= API_KEY)



"//////////////////////////////////// connexion aux BDD et API"




def generate_prompt(question : str, contexte : str):

    """
    #proposition 1)
    prompt pour le LLM générant la réponse finale en bout de pipeline, 
    on lui fourni la question et les articles "contexte" selectionnés par les pipeline relationnels et sémantiques
    """

    template = """Répond à cette question : {question} 
        en te servant des articles suivants contexte : 
        
        /// début du contexte

        {contexte} 
        
        /// fin du contexte

        
        Dans le contexte il y a plusieurs articles de loi dont certains sont utiles. Les articles sont séparés par : //////

        utilise les articles necessaires et utiles d'après la question pour formuler ta réponse.
        Si tu n'as aucun contexte pertinent répond "je ne sais pas" sinon, essaye de répondre avce ce que tu as sans inventer

        cite tes sources 
        
        rappel de la question :
        {question} """

    prompt = PromptTemplate.from_template(template)
    
    return prompt


def generate_prompt2(question, contexte):

    """
      #proposition 2)
    prompt pour le LLM dns le cas où le contexte est trop long. On ne conserve que les articles qui ne sont pas hors sujet.
    Le str en sortie sera utilisé comme contexte pour le prompt final (generate_prompt)
    """

    template = """Répond à cette question : {question} 

    Voici un contexte avec une suite d'articles qui peuvent être utiles ou nom à répondre à la question 
        
        /// début du contexte

        {contexte} 
        
        /// fin du contexte

       Dans le contexte, récupère les articles et passages qui ne sont pas hors sujet par rapport à la question et qui pourraient être utiles en support si on voulait rédiger une réponse. Ecris ta réponse comme ça :

        formalisme : 

       ///// nom de larticle : extrait pertinent
       ///// nom de larticle : extrait pertinent
       ///// nom de larticle : extrait pertinent
       ///// nom de larticle : extrait pertinent

       """

    prompt = PromptTemplate.from_template(template)
    
    return prompt



def generate_answer(question : str, adresse_vectorstore : str, k : int) -> str :

    """
    On fourni au LLM les articles selectionnés par les pipelines sémantiques et relationnels et il générère la réponse.
    Si le contexte est trop long, on demande à un LLM de choisir les articles les plus pertinents et on fournit de nouveau cette selection en contexte.
    """



    liste_semantique = pipeline_semantique(question, adresse_vectorstore, k)
    liste_relationnelle = pipeline_relationnel(question, llm)
   
    try :
        liste = liste_relationnelle + liste_semantique
        prompt = generate_prompt(question, liste)
        llm_chain = LLMChain(prompt=prompt, llm=llm)
        result = llm_chain.run(question=question, contexte=liste)

    except:
        if liste_semantique:
            milieu_sem = len(liste_semantique) // 2
            demi_liste_sem1 = liste_semantique[:milieu_sem]
            demi_liste_sem2 = liste_semantique[milieu_sem:]
        else:
            demi_liste_sem1 = []
            demi_liste_sem2 = []

    # Traiter liste_relationnelle
        if liste_relationnelle:
            milieu_rel = len(liste_relationnelle) // 2
            demi_liste_rel1 = liste_relationnelle[:milieu_rel]
            demi_liste_rel2 = liste_relationnelle[milieu_rel:]
        else:
            demi_liste_rel1 = []
            demi_liste_rel2 = []

        liste1 = demi_liste_sem1 + demi_liste_rel1
        liste2 = demi_liste_sem2 + demi_liste_rel2
        liste_recomposee = []
        for el in [liste1, liste2]:
            prompt = generate_prompt2(question, el)
            llm_chain = LLMChain(prompt=prompt, llm=llm)
            texte = llm_chain.run(question=question, contexte=el)
            liste_recomposee.append(texte)
        prompt = generate_prompt(question, liste_recomposee)
        llm_chain = LLMChain(prompt=prompt, llm=llm)
        result = llm_chain.run(question=question, contexte=liste_recomposee)
    return result

      

        
    
    

    return result






if __name__ == "__main__":

    question = "Que dit l'article 3 du code civil ?"
    reponse = generate_answer(question, adresse_vectorstore, 3)
    print(reponse)
