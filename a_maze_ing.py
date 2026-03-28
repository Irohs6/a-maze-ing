# Point d'entrée principal du programme A-Maze-ing.
# Ce fichier est le seul à appeler directement depuis la ligne de commande : python3 a_maze_ing.py config.txt
# Il lit l'argument config.txt, instancie le contrôleur principal (MazeController)
# et délègue toute la logique d'exécution à ce dernier.
# Il gère également les erreurs de haut niveau (argument manquant, fichier introuvable)
# et affiche un message d'aide à l'utilisateur en cas de mauvaise utilisation.

import sys
from model.config_parser import ConfigParser


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 a_maze_ing.py <config.txt>")
        sys.exit(1)

    config_file = sys.argv[1]
    print(f"Configuration loaded successfully: config = {config_file}")
    try:
        config_parser = ConfigParser(config_file)
        config = config_parser.parse()
        print(f"Configuration parsed successfully: {config}")
    except FileNotFoundError as error:
        print(error)
        sys.exit(1)
    except ValueError as error:
        print(f"Error in configuration file: {error}")
        sys.exit(1)


if __name__ == "__main__":
    main()
