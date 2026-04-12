# mazegen/kruksal.py

## Rôle
Algorithme de génération de labyrinthe **imparfait** (boucles possibles) inspiré de l'algorithme de Kruskal. Produit des labyrinthes avec plusieurs chemins possibles entre deux points.

## Ce qu'il fait
- Passe 1 : pour chaque cellule éligible (hors bordures, hors motif 42), supprime aléatoirement un mur
- Passe 2 (`_second_loop`) : réduit à 2 le nombre de murs de toutes les cellules intérieures qui en ont plus de 2
- Vérifie la validité du labyrinthe généré via `MazeValidator` après chaque tentative
- Réessaie jusqu'à `_MAX_GLOBAL_ATTEMPTS = 30` fois en cas d'échec de validation
- Copie profonde du labyrinthe (`copy.copy` + `grid` slice) pour ne pas corrompre l'état en cas d'échec
- Retourne le `track` des murs supprimés pour l'animation

## Note globale : 7/10

## Améliorations possibles
| Priorité | Amélioration |
|----------|-------------|
| Haute | 30 tentatives peuvent échouer silencieusement sur des grands labyrinthes — lever une exception explicite si toutes les tentatives échouent |
| Haute | L'algorithme ne ressemble pas vraiment à Kruskal (pas d'Union-Find) — renommer en `RandomWallRemover` ou `ImperfectGenerator` pour plus de clarté |
| Haute | Performances dégradées sur les grands labyrinthes (> 71×71) due à la re-validation complète à chaque tentative |
| Moyenne | `_second_loop` itère sur `_to_destroy` sans ordre déterministe (set) — peut donner des résultats différents même avec le même seed |
| Faible | Implémenter le vrai algorithme de Kruskal avec Union-Find pour une meilleure efficacité (O(E log E)) |
