# tests/test_maze_generator.py

## Rôle
Tests unitaires de l'API publique du module `MazeGenerator`. Valide la génération déterministe et la conformité des labyrinthes produits.

## Ce qu'il fait
- Vérifie l'initialisation : dimensions, seed, `track` vide, `forty_two_cells` vide, `perfect=True` par défaut
- Fixtures : `gen_backtracker` (11×11, seed=1, perfect=True) et `gen_kruskal` (11×11, seed=1, perfect=False)
- Génération Backtracker : instance `Maze` retournée, dimensions correctes, `track` non vide
- Génération Kruskal : mêmes assertions
- **Déterminisme** : même seed → même grille (`grid` identique)
- Validation via `MazeValidator` : les deux algorithmes produisent des labyrinthes valides
- `reset()` : la grille est bien réinitialisée (tous les murs fermés = 15)

## Note globale : 8.5/10

## Améliorations possibles
| Priorité | Amélioration |
|----------|-------------|
| Moyenne | Ajouter un test vérifiant qu'un labyrinthe parfait a exactement un chemin entre deux points quelconques (via `PathFinder`) |
| Moyenne | Tester la gestion du cas `MazeValidator` qui retourne `False` (mock ou seed qui force l'échec) |
| Faible | Tester des tailles non carrées (ex. 20×10) pour couvrir les cas rectangulaires |
| Faible | Vérifier que `get_solution()` lève bien une `ValueError` si appelé avant `generate()` |
