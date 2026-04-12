# controller/maze_controller.py

## Rôle
Orchestrateur central du projet (pattern MVC — couche Controller). Coordonne le chargement de la configuration, la génération du labyrinthe, la recherche du chemin et l'affichage.

## Ce qu'il fait
- Lit et valide la configuration via `ConfigFile.parse()`
- Instancie le `MazeGenerator` avec les paramètres (taille, seed, mode parfait)
- Instancie le `PathFinder` pour trouver le chemin entre l'entrée et la sortie
- Instancie la `TerminalView` pour l'affichage
- `run()` orchestre la séquence complète :
  1. `_load_config()` → parse le fichier de configuration
  2. `_create_gen()` → instancie `MazeGenerator`
  3. `_create_pathfinder()` → instancie `PathFinder`
  4. `_create_view()` → instancie `TerminalView`
  5. Instancie `Menu(self)` et délègue tout le cycle interactif à `menu._run()`
- `_update_objects()` est appelé depuis `Menu` après un changement de config pour resynchroniser générateur, pathfinder et vue

## Note globale : 7.5/10

## Améliorations possibles
| Priorité | Amélioration |
|----------|-------------|
| Haute | Les méthodes `_create_gen`, `_create_pathfinder`, `_create_view` peuvent être appelées dans le désordre depuis `Menu` : risque de désynchronisation. Regrouper en une `_build_pipeline()` |
| Haute | Aucune gestion d'erreur dans `_create_gen` / `_create_view` si `_config` est `None` (AttributeError silencieuse possible) |
| Moyenne | Couplage fort à `TerminalView` : instancier la vue dynamiquement selon la config (`VIEW=terminal` / `VIEW=mlx`) |
| Faible | Ajouter un type de retour explicite sur toutes les méthodes privées |
