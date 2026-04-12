# a_maze_ing.py

## Rôle
Point d'entrée principal du programme. C'est le seul fichier à lancer depuis la ligne de commande :
```
python3 a_maze_ing.py config.txt
```

## Dépendances
- `colorama` : pour la couleur du message d'au revoir (`Fore.BLUE`, `Style.RESET_ALL`)
- `controller.maze_controller.MazeController` : orchestre toute la logique

## Ce qu'il fait
- Vérifie qu'exactement un argument est fourni (le fichier de configuration)
- Instancie le `MazeController` avec le chemin du fichier config
- Délègue toute la logique à `controller.run()`
- Gère les erreurs de haut niveau :
  - `FileNotFoundError` : fichier de config introuvable
  - `ValueError` / `KeyError` : configuration invalide ou incomplète
  - `KeyboardInterrupt` : interruption par Ctrl+C — affiche `"Bye-bye 👋"` en bleu et termine proprement

## Note globale : 8.5/10

## Améliorations possibles
| Priorité | Amélioration |
|----------|-------------|
| Faible | Ajouter un flag `--version` pour afficher la version du programme |
| Faible | Supporter plusieurs fichiers config passés en argument |
| Faible | Ajouter un mode `--verbose` / `--debug` activant les logs |
| Faible | Remplacer `sys.exit(1)` par un code de sortie nommé (enum) pour plus de lisibilité |
