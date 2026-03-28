# Point d'entrée principal du programme A-Maze-ing.
# Ce fichier est le seul à appeler directement depuis la ligne de commande : python3 a_maze_ing.py config.txt
# Il lit l'argument config.txt, instancie le contrôleur principal (MazeController)
# et délègue toute la logique d'exécution à ce dernier.
# Il gère également les erreurs de haut niveau (argument manquant, fichier introuvable)
# et affiche un message d'aide à l'utilisateur en cas de mauvaise utilisation.
