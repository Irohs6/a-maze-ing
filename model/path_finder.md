# model/path_finder.py

## Rôle
Algorithme de recherche du/des plus court(s) chemin(s) dans le labyrinthe. Implémente un **BFS (Breadth-First Search)** optimisé avec détection des labyrinthes imparfaits.

## Ce qu'il fait
- `_compute_distance_and_predecessors()` : BFS depuis `entry`, construit le graphe des distances et des prédécesseurs avec élagage (arrêt dès que la distance de `exit` est connue)
- `_reconstruct_k_paths()` : remonte le graphe de prédécesseurs via DFS itératif (pile explicite, pas de récursion) pour extraire jusqu'à `k` plus courts chemins
- `_bfs_with_forbidden_edge(u, v)` : relance un BFS standard en interdisant une arête précise — permet de détecter des chemins alternatifs (cycles)
- `_find_extra_paths()` : applique le principe de Yen — interdit successivement chaque arête du plus court chemin pour trouver jusqu'à `n_extra` chemins alternatifs (même longueur ou plus longs)
- `_build_connections_dict(path)` : convertit une liste de directions en dictionnaire `{(x,y): {dirs ouvertes}}` pour le rendu visuel des jonctions
- `find_k_shortest_paths(k=1, n_extra=2)` : point d'entrée public — retourne une liste de dicts de connexions `[{(x,y): {dirs}}, ...]`
  - 1 plus court chemin (BFS) + jusqu'à `n_extra` chemins alternatifs
  - Si la sortie est inaccessible, retourne `[]`
  - `is_perfect = len(result) == 1` (aucun chemin alternatif trouvé)

## Note globale : 9.5/10

## Améliorations possibles
| Priorité | Amélioration |
|----------|-------------|
| Haute | Aucune gestion si `entry` ou `exit` sont hors des bornes du labyrinthe — lever une `ValueError` explicite |
| Moyenne | Complexité de `_find_extra_paths` : O(path_len × maze_cells) — documenter cette complexité dans la docstring |
| Faible | Ajouter un algorithme A* comme alternative pour les très grands labyrinthes (meilleure performance heuristique) |
| Faible | Exposer une méthode `find_path()` simple (alias `find_k_shortest_paths(k=1)[0]`) pour l'usage courant |
