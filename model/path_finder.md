# model/path_finder.py

## Rôle
Algorithme de recherche du/des plus court(s) chemin(s) dans le labyrinthe. Implémente un **BFS (Breadth-First Search)** optimisé.

## Ce qu'il fait
- Parcourt le labyrinthe en largeur depuis `entry` vers `exit`
- Élagage BFS : arrête l'exploration dès que la distance optimale est connue
- `find_k_shortest_paths(k)` : retourne les `k` plus courts chemins sous forme de listes de directions (`N`, `E`, `S`, `W`)
- Reconstruction itérative (pas récursive) — pas de risque de `RecursionError` sur de grands labyrinthes
- Construit un dictionnaire `path_connections` par cellule pour l'affichage des jonctions de chemin dans la vue

## Note globale : 9/10

## Améliorations possibles
| Priorité | Amélioration |
|----------|-------------|
| Haute | Aucune gestion si `entry` ou `exit` sont hors des bornes du labyrinthe — lever une `ValueError` explicite |
| Moyenne | `find_k_shortest_paths` peut être coûteux si `k` est grand sur un labyrinthe complexe — documenter la complexité |
| Moyenne | Ajouter un algorithme A* comme alternative pour les labyrinthes très grands (meilleure heuristique de direction) |
| Faible | Exposer une méthode `find_path()` simple (alias `find_k_shortest_paths(k=1)[0]`) pour l'usage courant |
