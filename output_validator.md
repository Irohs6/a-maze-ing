# output_validator.py

## Rôle
Script utilitaire de validation du fichier de sortie du labyrinthe. Vérifie que le fichier hexadécimal exporté est cohérent (murs symétriques entre cellules voisines).

## Ce qu'il fait
- Lit le fichier de sortie hex (`maze_output.txt`) passé en argument
- Parse chaque caractère hex en entier (0–15)
- Pour chaque cellule, vérifie la cohérence de ses 4 murs avec ses voisins directs :
  - cellule N/S : bit Sud de (r,c) == bit Nord de (r+1,c)
  - cellule E/W : bit Est de (r,c) == bit Ouest de (r,c+1)
- Affiche les coordonnées des cellules incorrectes

## Note globale : 5/10

## Améliorations possibles
| Priorité | Amélioration |
|----------|-------------|
| Haute | Aucune gestion d'erreur — plante si le fichier est malformé, vide ou inaccessible |
| Haute | Style de code très condensé (compréhensions imbriquées, variables à une lettre) — illisible pour la maintenance |
| Haute | Pas de code de retour : toujours `exit 0` même si des erreurs sont trouvées — ajouter `sys.exit(1)` si des erreurs sont détectées |
| Moyenne | Utiliser `argparse` à la place du check manuel `sys.argv` |
| Faible | Intégrer comme méthode de `MazeValidator` plutôt que script standalone |
