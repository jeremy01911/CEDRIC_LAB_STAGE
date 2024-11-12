from vectorbase.build_vectorbase import pipeline_build_vectorbase

from vars_connexion import model_kwargs, encode_kwargs, model, BDD, vectorstore


"//////////////////////////////////// connexion aux BDD et API"

adresse_vectorstore = vectorstore
adresse_BDD = BDD

"//////////////////////////////////// connexion aux BDD et API"


if __name__ == "__main__":
    pipeline_build_vectorbase(adresse_BDD, model_kwargs, encode_kwargs, model, adresse_vectorstore)