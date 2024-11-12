from chat_bot_xml.graph.parse_XML import find_start
from chat_bot_xml.graph.parse_XML import frst_file
from chat_bot_xml.graph.parse_XML import start_all
from vars_connexion import chemin_LEGI

"""
Lancer le parsing et l'ajout au BDD graph Neo4j
"""

point_depart = chemin_LEGI

def main(point_depart):
    start = point_depart
    new=find_start(start)
    files=frst_file(new)
    start_all(files)


if __name__ == "__main__":
    
    main(point_depart)
