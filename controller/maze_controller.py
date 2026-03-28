# controller/maze_controller.py — Orchestrateur central du programme.
# Contient la classe MazeController qui fait le lien entre le modèle et la vue.
# Responsabilités :
#   1. Recevoir le chemin du fichier de configuration depuis a_maze_ing.py
#   2. Instancier ConfigParser et lire la configuration
#   3. Instancier le générateur de labyrinthe (MazeGenerator depuis mazegen)
#      et déclencher la génération avec les paramètres de la config
#   4. Instancier PathFinder et calculer le chemin solution
#   5. Écrire le fichier de sortie au format hexadécimal requis
#   6. Instancier la vue appropriée (TerminalView ou MlxView) et lancer l'affichage
#   7. Gérer les actions utilisateur transmises par la vue (régénérer, afficher solution, etc.)
#   8. Propager les erreurs sous forme de messages clairs sans planter le programme.
