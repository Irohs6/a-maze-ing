# mazegen/algorithm.py

## Rôle
Classe abstraite de base pour tous les algorithmes de génération de labyrinthe. Applique le pattern **Template Method** via `ABC`.

## Ce qu'il fait
- Déclare la méthode abstracte `generate()` que chaque algorithme concret doit implémenter
- Stocke la référence au `Maze`, ses dimensions, les cellules du motif "42" et les cellules de bordure
- Fournit des helpers partagés par tous les algorithmes :
  - `_get_neighbors_of_cell(x, y)` : liste des voisins valides avec leur direction
  - `_get_direction_neighbor(x, y, direction)` : coordonnées du voisin dans une direction donnée
  - `_get_maze_boundaries()` : ensemble des cellules de bordure
- Expose la variable de classe `perfect: ClassVar[bool]` pour distinguer les algorithmes parfaits / imparfaits

## Note globale : 8/10

## Améliorations possibles
| Priorité | Amélioration |
|----------|-------------|
| Haute | `PATTERN_42` est défini dans `Maze` mais les sous-classes y accèdent indirectement via `maze.forty_two_cells` — harmoniser l'accès |
| Moyenne | Ajouter une méthode `reset()` abstraite pour permettre au `MazeGenerator` de réinitialiser sans recréer l'objet |
| Faible | Ajouter `__repr__` ou `__str__` pour faciliter le débogage |
| Faible | Documenter clairement l'interface attendue du `track` retourné par `generate()` |
