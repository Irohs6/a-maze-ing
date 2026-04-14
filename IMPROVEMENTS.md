# Améliorations à effectuer — A-Maze-ing

---

## `a_maze_ing.py`

- Ajouter la gestion de `SystemExit` propre (exit code distinct pour chaque type d'erreur plutôt que tout à `1`)
- Le `KeyboardInterrupt` affiche "Bye-bye" + emoji directement dans `main()` — déplacer ce message dans le controller ou une couche présentation
- Pas de logging : ajouter un appel au logger (`utils/logger.py`) pour tracer les erreurs au lieu de `print` brut

---

## `controller/maze_controller.py`

- Les attributs `_generator`, `_finder`, `_view`, `menu` sont créés dynamiquement après `__init__` — les initialiser à `None` explicitement dans `__init__` pour éviter des `AttributeError` potentiels
- `_create_pathfinder` et `_create_view` appellent `_generator.get_maze()` séparément — stocker le résultat une seule fois dans `run()`
- `run()` appelle `self.menu._run()` avec un accès direct à un membre privé — exposerun méthode publique `run()` sur `Menu`
- Pas de type annotations sur `_create_gen`, `_create_pathfinder`, `_create_view` — ajouter `-> None`
- `_config` peut être `None` avant `_load_config()` — annotations et guards manquants

---

## `model/maze.py`

- `PATTERN_42` est une constante de classe mais redéfinie comme attribut d'instance via `place_42_center` — peut créer de la confusion, passer en `ClassVar`
- `_is_42_wall` : logique inversée lisible mais verbeuse (`if not ... return False else return True`) — simplifier en `return ... in self.forty_two_cells`
- `remove_wall` lève `ValueError` même pour les bordures légitimes (ex: cellule en bord n'a pas de voisin) — clarifier le message d'erreur
- `encode_hex` construit une chaîne par concatenation `+=` dans une boucle — utiliser `"".join()`
- `_DIRECTIONS` est dupliqué à l'identique dans `Algorithm` et `PathFinder` — faire référence à une seule source (ex: constante dans un module partagé)
- `place_42_center` mutate à la fois `self.grid` et `self.forty_two_cells` — séparer les deux responsabilités

---

## `model/maze_validator.py`

- `_has_forbidden_open_areas` et `_validate_maze_connectivity` sont appelées depuis `Kruksal` directement (accès à méthodes privées depuis l'extérieur) — les rendre publiques ou exposer une méthode dédiée
- Pas de message d'erreur retourné (`validate()` retourne `bool`) — envisager de retourner une liste d'erreurs pour faciliter le debug
- La vérification 42-pattern dans `_validate_42_pattern` ne vérifie que la présence de cellules dans `forty_two_cells` — ne valide pas que le motif visuel est intact après la génération

---

## `model/config_file.py`

- `_parse_line` gère le cas `VIEW` mais cette clé n'est ni dans `REQUIRED_KEYS` ni `OPTIONAL_KEYS` — dead code ou feature incomplète à trancher
- `_parse_optionals` utilise une walrus operator dans un `for` sur `OPTIONAL_KEYS` mais génère le `SEED` via `time_ns()` même si fourni — risque de collision si mal ordonné
- `ENTRY` et `EXIT` sont parsés en `tuple(int(v) for v in str.split(","))` sans vérifier qu'il y ait exactement 2 valeurs — peut lever un `ValueError` obscur
- Le `model_validator` `validate_entry_exit_bounds` est une contrainte métier — documenter clairement pourquoi la borne est `< WIDTH` et non `<= WIDTH`

---

## `mazegen/algorithm.py`

- `_DIRECTIONS` dupliqué depuis `Maze` — utiliser `Maze._DIRECTIONS` directement ou extraire dans un module `constants.py`
- `_get_direction_neighbor` est présente ici ET dans `Maze` ET dans `PathFinder` — factoriser
- `perfect: ClassVar[bool]` est déclaré mais pas enforced par ABC (pas de `@property` abstraite) — un sous-classe oubliant de définir `perfect` n'est pas détectée à l'instantiation

---

## `mazegen/backtracker.py`

- L'algorithme démarre toujours depuis `(0, 0)` — paramètre `start` devrait être configurable
- `visited = set(self.maze.forty_two_cells)` initialise les cellules 42 comme visitées sans commentaire — ajouter un commentaire explicatif
- Pas de vérification que le labyrinthe est connexe après la génération (contrairement à `Kruksal`) — ajouter la validation ou la déléguer à `MazeGenerator`

---

## `mazegen/kruksal.py`

- `_MAX_GLOBAL_ATTEMPTS = 30` et la limite interne `50` sont des magic numbers non documentés — extraire en constantes nommées avec justification
- La boucle `while not validator...` peut tourner 50 × 30 = 1 500 fois dans le pire cas sans feedback — ajouter un log ou un warning
- `copy.copy` + copie manuelle de `grid` (ligne par ligne) au lieu de `copy.deepcopy` — utiliser `deepcopy` directement pour éviter les bugs de copie partielle
- `_second_loop` modifie `maze` en place ET retourne le tuple `(maze, tracks)` — interface incohérente, choisir l'un ou l'autre

---


## `view/menu.py`

- `_get_key` lit stdin en mode raw puis restaure via `termios.tcsetattr` — utiliser `raw_stdin()` de `ansi_utils` pour éviter la duplication
- `_settings` est une fonction de 100+ lignes à découper en sous-fonctions (une par champ)
- La validation Pydantic dans `_settings` est faite à la fin seulement — valider au fur et à mesure pour un feedback immédiat
- `self.fd` et `self.old` exposés comme attributs d'instance alors qu'ils ne servent qu'à `_get_key` — les garder locaux à cette méthode
- Pas de gestion de `KeyboardInterrupt` dans `_settings` — Ctrl+C sort sans restaurer l'état de la config

---

## `utils/logger.py`

- Fichier vide — implémenter un logger minimal (wrapping de `logging` standard) ou supprimer le fichier et le module `utils/`
- Si implémenté, centraliser tous les `print` d'erreur du projet pour pouvoir activer/désactiver le mode verbose

---

## `tests/`

- Les tests unitaires (`test_maze.py`, `test_path_finder.py`, etc.) méritent d'être exécutés en CI — ajouter une target `make test` dans le Makefile
- Pas de tests pour `terminal_renderer.py` ni `menu.py` — difficile à tester unitairement, mais des smoke tests d'intégration seraient utiles
- Couverture de code non mesurée — ajouter `coverage` dans `requirements.txt` et `make coverage`
