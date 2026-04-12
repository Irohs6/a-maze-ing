# tests/test_maze_validator.py

## Rôle
Tests unitaires du `MazeValidator`. Vérifie que chaque règle de validation détecte correctement les labyrinthes invalides.

## Ce qu'il fait
- Teste chaque check individuellement : valeurs de cellules, bordures, symétrie, zones 3×3, connectivité, motif 42
- Construit des labyrinthes manuellement avec des défauts spécifiques pour déclencher chaque erreur
- Vérifie qu'un labyrinthe valide généré par `Backtracker` passe tous les checks
- Couvre les cas limites : labyrinthe minimal, labyrinthe trop petit pour le motif 42

## Note globale : 8/10

## Améliorations possibles
| Priorité | Amélioration |
|----------|-------------|
| Moyenne | Une fois que `validate()` retourne un objet résultat (et non un `bool`), tester précisément quel check a échoué |
| Moyenne | Ajouter des tests sur les zones 3×3 ouvertes avec des configurations aux limites (zone de taille exactement 3×3) |
| Faible | Tester la performance du validator sur un labyrinthe de grande taille (101×101) |
| Faible | Utiliser `@pytest.mark.parametrize` pour les tests de valeurs de cellules invalides (0→15 valid, -1 et 16 invalides) |
