# mazegen/maze_generator.py

## Rôle
Façade du module de génération de labyrinthe. Expose une API publique propre et réutilisable qui masque le choix de l'algorithme interne.

## Ce qu'il fait
- Sélectionne automatiquement l'algorithme selon `perfect=True` (Backtracker) ou `perfect=False` (Kruksal)
- Initialise le `Maze` et le `random.seed`
- Appelle `algo.generate()` et valide le résultat via `MazeValidator`
- `get_maze()` : retourne l'instance `Maze` générée
- `get_solution()` : retourne le chemin solution (liste de directions)
- `reset(seed)` : réinitialise complètement le générateur pour un nouveau labyrinthe
- Lève une `ValueError` si le labyrinthe généré est invalide

## Note globale : 8.5/10

## Améliorations possibles
| Priorité | Amélioration |
|----------|-------------|
| Haute | `get_solution()` lève une `ValueError` si appelé avant `generate()` — mais `generate()` ne calcule pas la solution (c'est `PathFinder` qui le fait) : la méthode est trompeuse |
| Moyenne | `_build_algorithm()` utilise `for...else` avec `raise` — le `else` est inutile ici, simplifier avec un `raise` indépendant |
| Moyenne | Pas de timeout sur la génération Kruskal qui peut prendre plusieurs secondes pour de grands labyrinthes |
| Faible | Permettre d'enregistrer des algorithmes customisés via un registre (pattern Strategy extensible) |
