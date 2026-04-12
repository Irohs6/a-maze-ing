# mazegen/backtracker.py

## Rôle
Algorithme de génération de labyrinthe **parfait** (un seul chemin entre deux points quelconques) basé sur le **DFS récursif iteratif (Recursive Backtracker)**.

## Ce qu'il fait
- Génère un labyrinthe parfait en parcourant chaque cellule en profondeur
- Utilise une pile (stack) pour revenir en arrière quand toutes les cellules voisines ont été visitées
- Exclut les cellules du motif "42" de la visite dès l'initialisation (`visited = set(maze.forty_two_cells)`)
- Retourne le `track` : liste de triplets `(x, y, direction)` enregistrant chaque mur supprimé (utilisé pour l'animation)
- Garantit que toutes les cellules non-42 sont connectées

## Note globale : 8.5/10

## Améliorations possibles
| Priorité | Amélioration |
|----------|-------------|
| Moyenne | Le point de départ est toujours `(0, 0)` — permettre de passer une cellule de départ arbitraire pour plus de flexibilité |
| Moyenne | Aucune gestion si la cellule `(0,0)` fait partie du motif 42 (edge case très grand motif) |
| Faible | Ajouter un paramètre `bias` pour orienter préférentiellement l'exploration (ex. biais horizontal/vertical pour des labyrinthes au look différent) |
| Faible | Le shuffle implicite de `random.choice` est uniforme — documenter l'impact du seed sur la reproductibilité |
