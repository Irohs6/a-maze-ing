# view/menu.py

## Rôle
Interface de menu interactif en terminal. Permet à l'utilisateur de naviguer entre les options, modifier les paramètres du labyrinthe et lancer la génération/affichage.

## Ce qu'il fait
- Affiche un menu vertical naviguable (flèches haut/bas + Entrée) avec 3 options : **Generate Maze**, **Settings**, **Exit**
- Met en évidence l'option sélectionnée (fond rouge via `colorama`)
- **Mode "Settings"** (`_settings()`) : demande interactivement via `click.prompt` tous les paramètres :
  - `WIDTH`, `HEIGHT` (IntRange 4–100)
  - `ENTRY` (x, y avec bornes 0–WIDTH/HEIGHT)
  - `EXIT` (x, y avec bornes 0–WIDTH/HEIGHT)
  - `OUTPUT_FILE` (str)
  - `PERFECT` (confirm oui/non)
  - `SEED` (int ≥ 0, défaut = `time.time_ns()`)
  - Valide avec Pydantic (`ConfigFile`) avant application — affiche les erreurs détaillées sans crasher
  - Permet de réessayer en cas d'erreur de validation (`press Enter to retry`)
  - Abandonne proprement si l'utilisateur appuie sur Ctrl+C (`click.exceptions.Abort`)
- **Mode "Generate"** (`_execute()`) :
  - Génère le labyrinthe via `MazeController._generator.generate()`
  - Calcule jusqu'à 3 chemins via `PathFinder.find_k_shortest_paths(k=3)`
  - Affiche et anime la solution via `TerminalView.show_solution()`
  - Écrit le résultat encodé (hex + ENTRY + EXIT) dans `OUTPUT_FILE`
  - Affiche la sortie dans le terminal, attend Entrée puis réinitialise avec un nouveau seed
- **Gestion du terminal** : hide/show cursor (`\033[?25l` / `\033[?25h`), bloc `try/finally` pour toujours restaurer le curseur même en cas d'exception
- `_update_objects()` : resynchronise générateur, pathfinder et vue après changement de config
- Conserve une copie profonde (`deepcopy`) de la config initiale comme référence

## Note globale : 8.5/10

## Améliorations possibles
| Priorité | Amélioration |
|----------|-------------|
| Haute | Le mode raw `tty.setraw` dans `_get_key()` n'est pas protégé par un `try/finally` systématique si `_settings()` crash — risque de terminal cassé |
| Haute | Le menu est limité à 3 options hardcodées — rendre la liste d'options configurable/extensible |
| Moyenne | Mélange de responsabilités : lecture d'input + affichage + logique de navigation dans la même classe |
| Moyenne | La copie `_copy_config` est créée mais jamais utilisée pour rollback — implémenter un vrai mécanisme d'annulation des paramètres |
| Faible | Ajouter une confirmation « Êtes-vous sûr ? » avant de quitter |
