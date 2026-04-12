# model/maze_validator.py

## Rôle
Validateur de structure du labyrinthe, séparé de `Maze` pour respecter le **Principe de Responsabilité Unique (SRP)**. Vérifie l'intégrité complète d'une instance `Maze` avant utilisation.

## Ce qu'il fait
Exécute 6 contrôles en séquence via `validate()` :
1. **Valeurs des cellules** : chaque cellule est dans `[0, 15]`
2. **Bordures fermées** : toutes les cellules de bordure ont un mur sur leur face extérieure
3. **Symétrie des murs** : si la cellule (x,y) a un mur Est, alors (x+1,y) a un mur Ouest (et vice-versa)
4. **Pas de zones 3×3 ouvertes** : aucune zone entièrement libre de 3×3 cellules
5. **Connectivité** : toutes les cellules (hors motif "42") sont accessibles via BFS depuis la première cellule non-42
6. **Présence du motif "42"** : les cellules isolées du pattern 42 sont bien à la valeur `15`

## Note globale : 9/10

## Améliorations possibles
| Priorité | Amélioration |
|----------|-------------|
| Haute | `validate()` retourne un simple `bool` sans indiquer quel test a échoué — retourner un objet résultat avec un message d'erreur détaillé |
| Moyenne | Le check de connectivité est O(n) mais peut être lent sur de très grands labyrinthes — acceptable, mais peut être combiné avec la génération |
| Faible | Permettre de désactiver certains checks individuellement (ex. ignorer le check 42 pour les labyrinthes custom) |
| Faible | Ajouter un check sur l'existence de `ENTRY` et `EXIT` accessibles (pas isolated) |
