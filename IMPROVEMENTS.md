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

## `view/terminal_renderer.py`

- `_draw_grid` recalcule `ch`, `total_cols`, `total_rows` et définit `_wall_char` à chaque appel — si `cell_width=1` est toujours utilisé, ces calculs sont inutilement redondants
- `_draw_final` contient maintenant la boucle interactive `raw_stdin` — cette responsabilité devrait être dans `TerminalView` ou `terminal_spawn_runner`, pas dans le renderer pur
- `_build_cell_buf` reçoit `ft` et `forty_two_color` mais ne les utilise plus depuis la refacto — supprimer ces paramètres devenus inutiles
- `COLOR_THEMES` et `COLOR_THEMES_42` sont de longueurs égales mais rien ne le garantit — ajouter un `assert len(COLOR_THEMES) == len(COLOR_THEMES_42)` en tête de module
- `_BOX_PATH` doit avoir exactement 16 caractères (index 0–15) — ajouter un `assert len(_BOX_PATH) == 16`

---

## `view/terminal_view.py`

- `show_solution` appelle `_spawn_solution_window` avec `tracks` mais `_draw_final` ignore maintenant `forty_two_color` en interne — la valeur passée en fallback est inutile
- Le fallback `input("\nAppuie sur Entrée pour quitter…")` est mort code depuis que `_draw_final` gère la boucle interactive elle-même — à supprimer
- `track` dans `__init__` est stocké mais jamais utilisé dans la classe — supprimer ou implémenter
- Pas de gestion du cas `all_paths = []` dans `show_solution` (lève une `IndexError` sur `all_paths[0]`) — déjà partiellement géré mais la condition `if all_paths else []` mérite un guard plus clair

---

## `view/terminal_launcher.py`

- Le fichier JSON temporaire est supprimé dans `_load_config` (dans le runner) mais jamais supprimé si le Popen échoue avant lancement — ajouter un `try/finally` ou `NamedTemporaryFile` avec `delete=True`
- `zoom: float = 0.28` est un magic number qui dépend de la taille des caractères de l'émulateur — documenter ou rendre configurable
- Pas de timeout sur le `Popen` enfant — si le terminal ne démarre pas, le parent ne le sait pas

---

## `view/terminal_spawn_runner.py`

- La boucle `_run_interaction` recrée tout le rendu pour [C] avec `delay=0` — si le labyrinthe est grand, ça peut flasher. Envisager un double-buffer ou un redraw partiel
- `_show_hint` écrit sur stdout sans ANSI de positionnement — peut écraser du contenu si le terminal est redimensionné
- Le thème 42 (`theme_idx_42`) est cyclé indépendamment de `theme_idx` mais commence toujours synchronisé — si les listes ont des longueurs différentes, la synchro se perd

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
