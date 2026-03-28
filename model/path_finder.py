# model/path_finder.py — Algorithme de recherche du chemin le plus court.
# Contient la classe PathFinder qui opère sur une instance de Maze.
# Implémente un algorithme BFS (Breadth-First Search) pour trouver
# le chemin valide le plus court entre l'entrée et la sortie.
# Fournit des méthodes pour :
#   - calculer et retourner le chemin sous forme de liste de directions (N, E, S, O)
#   - vérifier l'accessibilité globale du labyrinthe (toutes les cellules atteignables)
#   - vérifier l'unicité du chemin si PERFECT=True
# Le résultat est utilisé à la fois pour l'écriture dans le fichier de sortie
# et pour l'affichage visuel de la solution.
