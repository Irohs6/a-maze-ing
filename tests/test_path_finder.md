# tests/test_path_finder.py

## Rôle
Tests unitaires de l'algorithme de recherche de chemin `PathFinder`. Vérifie la correction du BFS et le format des résultats.

## Ce qu'il fait
- Construit des labyrinthes simples manuellement (couloir 3×1, couloir 1×3, labyrinthe 3×3 à deux chemins)
- Vérifie que le chemin trouvé relie effectivement l'entrée à la sortie
- Teste que le chemin retourné est bien le **plus court**
- Vérifie que le format de sortie contient uniquement des lettres `N`, `E`, `S`, `W`
- Teste la reproductibilité avec un seed fixe sur un labyrinthe généré
- Cas limites : labyrinthe non connexe (chemin impossible)

## Note globale : 9/10

## Améliorations possibles
| Priorité | Amélioration |
|----------|-------------|
| Faible | Tester `find_k_shortest_paths(k=2)` et vérifier que les deux chemins retournés ont la même longueur sur un labyrinthe à deux chemins |
| Faible | Tester la construction de `path_connections` et vérifier que les jonctions affichées sont correctes |
| Faible | Ajouter un test sur un grand labyrinthe (51×51) pour vérifier l'absence de `RecursionError` |
| Faible | Tester le cas `entry == exit` (chemin vide ou erreur) |
