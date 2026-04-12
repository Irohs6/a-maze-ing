# tests/test_maze_generator.py

## Rôle
Tests unitaires de l'API publique du module `MazeGenerator`. Valide la génération déterministe et la conformité des labyrinthes produits.

## Ce qu'il fait
- Vérifie l'initialisation avec différents paramètres (Backtracker vs Kruskal via `perfect=True/False`)
- Teste la **déterminisme** : même seed → même labyrinthe
- Vérifie que `get_maze()` retourne une grille aux bonnes dimensions
- Teste `reset()` : régénère correctement avec une nouvelle graine
- Valide les labyrinthes générés via `MazeValidator`
- Teste les paramètres invalides

## Note globale : 8/10

## Améliorations possibles
| Priorité | Amélioration |
|----------|-------------|
| Moyenne | Ajouter un test vérifiant qu'un labyrinthe parfait a exactement un chemin entre deux points quelconques |
| Moyenne | Tester la gestion du cas `MazeValidator` qui retourne `False` (mock ou seed qui force l'échec) |
| Faible | Tester des tailles non carrées (ex. 20×10) pour couvrir les cas rectangulaires |
| Faible | Vérifier que `get_solution()` lève bien une `ValueError` si appelé avant `generate()` |
