# jurai-jeremy : mise en place d'un chat_bot basé sur les technologies RAG



## Contexte

** Ce repo contient le travail effectué au cours du stage de Jérémy Tournellec au sein du laboratoire CEDRIC du conservatoire national des arts et metiers pour le projet JURAI. **

L'objectif était d'étudier l'intéret d'utiliser un système RAG pour la recherche d'informations juridiques Françaises.
Dans le dossier chat_bot_xml on retrouvera le code d'un chat_bot mis au point au cours de ce stage ayant pour but de répondre à des questions juridiques sur les articles codifiés et non codifiés du droit Français.

## environnement et installations

### environnement Python

```
git clone https://gitlab.com/mimounicnam/jurai-jeremy.git
cd jurai-jeremy
python -m venv env
source env/bin/activate
pip install -r requirements.txt

```

### Installation de Neo4j 

1. Téléchargez et installez Neo4j Desktop
2. Suivez les instructions d'installation pour votre système d'exploitation.
3. cliquer sur "New project" puis "local DMBS", l'activer avec le password : "password"

### base LEGI

La base LEGI est une base de données de fichier XML mise à jour régulièrement par la DILA.
La demande d'accès peut être faite auprès de cet e-mail : 

```
donnees-dila@dila.gouv.fr
```

Pour utiliser le code de chat_bot_xml il faut disposer un dossier en local contenant cette base de données

## chat_bot_xml

### description


L'émergence récente des LLM et la commercialisation de chat_GPT ont permis une révolution dans le domaine de  le recherche d'information. De nombreux travaux visent à utiliser ces technologies pour répondre à des questions complexes sur des sujets parfois précis.
Néanmoins, les LLM sont limité par le phénomène d'ahllucination. La capacité générative d’un modèle étant purement statistique, il peut être amené à fournir des réponses très fluides et crédibles mais factuellement fausses.

Pour contrer cette limité, des travaux récents ont proposé les pipelines RAG (retrieval augmented generation).
Le pipeline RAG pour la recherche d’informations repose sur la vectorisation de questions et de différentes sources textuelles avec un même modèle d’embedding qui capture le sens des phrases, leurs subtilités sémantiques, et les représente sous forme de vecteurs dans un même espace vectoriel. Grâce à cosine similarity on peut donc identifier les chunks de textes les plus sémantiquement proches d’une question données et les fournir en support en entrée à un LLM pour qu’il rédige une réponse sourcée et fiable. 

Bien que les systèmes RAG soient performants avec des questions et contextes riches sémantiquement, ils ont plus de mal avec des questions plus relationnelles avec un contexte pauvre. En effet, les embeddings ont du mal à capturer les nuances sémantiques de telles questions.

** on propose donc ici un système avec deux pipelines fonctionnant en parallèle : **

- un pipeline RAG classique basé sur l'embedding avec le modèle entence-croissant-LLM-base v0.4
- un pipeline relationnel qui extrait les références directesà des articles de droit dans les questions, et fourni au LLM le contenu des articles comme contexte. Les requêtes relationnelles sont menées dans une base de données graph construite avec Neo4j.



### pipeline

![Questions relationnelles et sémantiques](chat_bot_xml/images/questions.png)

![Pipeline RAG](chat_bot_xml/images/RAG2.png)

![Pipeline relationnel](chat_bot_xml/images/relational.png)

![Système complet](chat_bot_xml/images/all2.png)


### comment utiliser

chat_bot_xml contient 3 dossiers importants et un script de connexion : 

1. ** vectorbase ** : construction du vectorstore, il faut run "main_vectorbase".
2. ** graph ** : construction du graph databse, il faut run "main_graph".
3. ** QA ** : utilisation du pipeline, il faut rentrer une question dans le scipt "main_answer" et run ce script. Il faut au préalable avoir construit le vectorstore et le graph database.
4. ** vars_connexion ** : - il faut adapter les chemins locaux de la base de donnée relationnelle, du dossier LEGI et du vectorstore avant de peupler le graph et le vectorstore.
                          - il faut modifier les clefs des API des LLM (OPENAI et DEEPINFRA Llama) pour qu'ils puissent formuler une réponse.



## auteurs et remerciements


Projet mené dans le cadre d'un stage de 2eme année par Jérémy Tournellec, enadré par Nada Mimouni et Raphaël Fournier S'niehotta 


