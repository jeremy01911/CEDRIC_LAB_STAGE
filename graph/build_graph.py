from typing import List, Tuple, Union
from py2neo import Graph, Node, Relationship
from vars_connexion import NEO4J_URL, NEO4J_AUTH

"""
Fonctions pour ajouter dans un graph les liens entre un article et ses relations.

adding_in_graph : est appelé dans parse_XML à chaque fois qu'un nouvel article est parsé.
parser_or_not : Fonction pour vérifier l'existence d'un noeud dans le graph
"""

def get_or_create_node(graph: Graph, ID: Union[int, str], name: str) -> Node:
    """
    Ajouter un noeud dans le graph si il n'existe pas
    """
    result = graph.run("MATCH (a:Article {ID: $id}) RETURN a", id=ID)
    if not result.data():
        node = Node("Article", ID=ID, name=name)
        graph.create(node)
        return node
    else:
        return graph.nodes.match("Article", ID=ID).first()



def create_relationship(graph: Graph, node1: Node, relationship_type: str, node2: Node) -> None:
    """
    Créer une relation d'un certain type entre deux noeuds
    """
    relationship = Relationship(node1, relationship_type, node2)
    graph.create(relationship)



def adding_in_graph(ID: Union[int, str], name: str, refs_cible: List[Tuple[str, Union[int, str], str]], refs_source: List[Tuple[str, Union[int, str], str]]) -> None:
    """
   1) Ajout de l'article courant dans le graph
   2) ajout des articles en relations dans le graph
   3) ajout des liens entre l'article courant et ses relations dans le graph
    """
    node = get_or_create_node(graph, ID, name) #article courant
    
    for ref in refs_source:
        ref_type, ref_id, ref_name = ref
        ref_node = get_or_create_node(graph, ref_id, ref_name)
        create_relationship(graph, node, ref_type, ref_node)

    for ref in refs_cible:
        ref_type, ref_id, ref_name = ref
        ref_node = get_or_create_node(graph, ref_id, ref_name)
        create_relationship(graph, ref_node, ref_type, node)



def parser_or_not(graph: Graph, ID: Union[int, str]) -> str:
    """
    Indique si cet article a déjà été parsé pour ne pas perdre de temps à le reparser.
    """
    result = graph.run("MATCH (a:Article {ID: $id}) RETURN a", id=ID)
    if not result.data():
       return 'NO'
    else:
        return 'YES'

