# controller/maze_controller.py

## Rôle
Orchestrateur central du projet (pattern MVC — couche Controller). Coordonne le chargement de la configuration, la génération du labyrinthe, la recherche du chemin et l'affichage.

## Ce qu'il fait
- Lit et valide la configuration via `ConfigFile.parse()`
- Instancie le `MazeGenerator` avec les paramètres (taille, seed, mode parfait)
- Instancie le `PathFinder` pour trouver le chemin entre l'entrée et la sortie
- Instancie la `TerminalView` pour l'affichage
- Lance le menu interactif (`Menu`) qui pilote tout le cycle générer / afficher / rejouer

## Note globale : 7/10

## Améliorations possibles
| Priorité | Amélioration |
|----------|-------------|
| Haute | Les méthodes `_create_gen`, `_create_pathfinder`, `_create_view` sont appelées séparément via `Menu` : risque de désynchronisation si l'ordre n'est pas respecté. Regrouper en une seule méthode `_build_pipeline()` |
| Haute | Aucune gestion d'erreur dans `_create_gen` / `_create_view` si `_config` est `None` (AttributeError silencieuse possible) |
| Moyenne | Couplage fort à `TerminalView` : instancier la vue dynamiquement selon la config (`VIEW=terminal` / `VIEW=mlx`) |
| Faible | Ajouter un type de retour explicite sur toutes les méthodes privées |
