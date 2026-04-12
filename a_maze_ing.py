# Point d'entrée principal du programme A-Maze-ing.
# Ce fichier est le seul à appeler directement depuis la ligne de commande :
#   python3 a_maze_ing.py config.txt
# Il lit l'argument config.txt, instancie le contrôleur principal
# (MazeController) et délègue toute la logique d'exécution à ce dernier.
# Il gère également les erreurs de haut niveau
# (argument manquant, fichier introuvable) et affiche un message d'aide
# à l'utilisateur en cas de mauvaise utilisation.

import sys
from colorama import Fore, Style
from controller.maze_controller import MazeController


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python3 a_maze_ing.py <config.txt>")
        sys.exit(1)

    try:
        controller = MazeController(sys.argv[1])
        controller.run()
    except FileNotFoundError as error:
        print(error)
        sys.exit(1)
    except (ValueError, KeyError) as error:
        print(f"Error in configuration file: {error}")
        sys.exit(1)
    except KeyboardInterrupt:
        print(Fore.BLUE + "Bye-bye" + Style.RESET_ALL, end="")
        print("👋")
        sys.exit(1)


if __name__ == "__main__":
    main()
