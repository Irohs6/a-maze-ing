# tests/test_maze.py

## Rôle
Tests unitaires de la structure de données `Maze`. Vérifie toutes les opérations de manipulation de la grille et des murs.

## Ce qu'il fait
- Vérifie l'initialisation : dimensions correctes, toutes les cellules à `15` (4 murs fermés)
- Teste `has_wall()`, `set_wall()`, `remove_wall()` dans les 4 directions
- Vérifie la symétrie des murs : supprimer un mur côté Est supprime aussi le mur Ouest du voisin
- Teste le placement du motif "42" au centre : cellules occupées, taille minimale requise
- Vérifie les cas limites : labyrinthe 1×1, labyrinthe trop petit pour le motif 42

## Note globale : 8.5/10

## Améliorations possibles
| Priorité | Amélioration |
|----------|-------------|
| Moyenne | Tester `remove_wall()` sur les murs de bordure (comportement attendu : ValueError ou no-op ?) |
| Moyenne | Ajouter des tests pour `_cell_wall_count()` et `_is_border_wall()` |
| Faible | Tester l'encodage hex de la grille (`encode()` / sortie fichier) |
| Faible | Utiliser `@pytest.mark.parametrize` pour les tests directionnels (N/E/S/W) |
