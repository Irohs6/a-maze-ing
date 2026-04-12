# model/maze.py

## Rôle
Structure de données centrale du projet. Représente le labyrinthe comme une grille 2D de cellules encodées sur 4 bits.

## Ce qu'il fait
- Stocke la grille dans `grid[y][x]` (liste de listes d'entiers)
- Encode les murs de chaque cellule : bit 0 = Nord, bit 1 = Est, bit 2 = Sud, bit 3 = Ouest
- Fournit `has_wall()`, `set_wall()`, `remove_wall()` pour manipuler les murs de façon symétrique (supprime le mur des deux côtés)
- Place automatiquement le motif pixelisé "42" au centre du labyrinthe (si la taille le permet) via `place_42_center()` appelé dans `__init__`
- `encode_hex()` : exporte la grille en chaîne hexadécimale (une ligne par rangée, valeur `0–F` par cellule)
- Expose des helpers utilitaires : `_cell_wall_count()`, `_is_border_wall()`, `_is_42_wall()`, `_get_neighbors_of_cell()`, `_get_maze_boundaries()`

## Note globale : 8.5/10

## Améliorations possibles
| Priorité | Amélioration |
|----------|-------------|
| Haute | `remove_wall()` lève une `ValueError` sur les murs de bordure au lieu de les ignorer silencieusement — le comportement est incohérent avec `set_wall()` |
| Moyenne | `PATTERN_42` est défini dans `Maze` mais dupliqué implicitement dans les logiques des algorithmes — accès indirect via `maze.forty_two_cells` |
| Moyenne | `place_42_center()` est appelée dans `__init__` mais modifie l'état (`grid`) — séparer initialisation et placement pour faciliter le test unitaire |
