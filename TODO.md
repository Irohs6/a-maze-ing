# A-Maze-ing — TODO / Planning

## Vue d'ensemble

| #  | Étape                                  | Durée estimée | Dépend de |
|----|----------------------------------------|---------------|-----------|
| 1  | Configuration de l'environnement       | 30 min        | —         |
| 2  | `model/config_parser.py`               | 1h30          | —         |
| 3  | `model/maze.py`                        | 2h            | —         |
| 4  | `mazegen/maze_generator.py`            | 4h–6h         | #3        |
| 5  | `model/path_finder.py`                 | 1h30          | #3        |
| 6  | Écriture du fichier de sortie          | 1h            | #4, #5    |
| 7  | `controller/maze_controller.py`        | 1h30          | #2–#6     |
| 8  | `a_maze_ing.py` (point d'entrée)       | 30 min        | #7        |
| 9  | `view/terminal_view.py`                | 2h–3h         | #3, #5    |
| 10 | `view/mlx_view.py` (graphique)         | 3h–4h         | #3, #5    |
| 11 | Packaging `mazegen` (.whl / .tar.gz)   | 1h            | #4        |
| 12 | Makefile                               | 30 min        | #1        |
| 13 | README.md                              | 1h30          | Tout      |
| 14 | Lint, mypy, tests finaux               | 1h–2h         | Tout      |
|    | **TOTAL ESTIMÉ**                       | **~20h–25h**  |           |

---

## Détail des étapes

### Étape 1 — Configuration de l'environnement (30 min)
- [ ] Créer un virtualenv (`python3 -m venv .venv`)
- [ ] Installer les dépendances : `pip install -r requirements.txt`
- [ ] Vérifier que `flake8`, `mypy`, `pytest` fonctionnent
- [ ] Compléter le `.gitignore` (ajouter `.venv/`, `__pycache__/`, etc.)
- [ ] Premier commit : `chore: scaffold project structure`

---

### Étape 2 — `model/config_parser.py` (1h30)
- [ ] Classe `ConfigParser` avec méthode `parse(filepath: str)`
- [ ] Lire le fichier ligne par ligne, ignorer les commentaires (`#`)
- [ ] Extraire les paires `CLE=VALEUR`
- [ ] Valider les clés obligatoires : `WIDTH`, `HEIGHT`, `ENTRY`, `EXIT`, `OUTPUT_FILE`, `PERFECT`
- [ ] Convertir les types : `int` pour dimensions, `tuple(int,int)` pour coordonnées, `bool` pour PERFECT
- [ ] Vérifier que ENTRY et EXIT sont dans les limites `(0..WIDTH-1, 0..HEIGHT-1)`
- [ ] Vérifier que ENTRY ≠ EXIT
- [ ] Gérer les clés optionnelles : `SEED`, `ALGORITHM` (avec valeurs par défaut)
- [ ] Lever des exceptions claires pour chaque type d'erreur
- [ ] Écrire les tests dans `tests/test_config_parser.py`
- [ ] Commit : `feat: implement config file parser with validation`

---

### Étape 3 — `model/maze.py` (2h)
- [ ] Classe `Maze` avec grille 2D (`list[list[int]]`) de cells 4 bits (N=0, E=1, S=2, W=3)
- [ ] `__init__(width, height)` : initialiser toutes les cellules avec 4 murs fermés (`0xF`)
- [ ] Méthodes d'accès aux murs :
  - `has_wall(x, y, direction) -> bool`
  - `remove_wall(x, y, direction)` — supprime le mur ET le mur symétrique du voisin
  - `add_wall(x, y, direction)` — ajoute le mur ET le mur symétrique
- [ ] `is_valid() -> bool` : vérifier la cohérence des murs entre cellules voisines
- [ ] `has_open_3x3() -> bool` : détecter les zones 3×3 sans murs (interdit)
- [ ] `to_hex() -> list[str]` : encoder chaque ligne en chaîne hexadécimale
- [ ] Getters : `width`, `height`, accès à une cellule `cell(x, y)`
- [ ] Écrire les tests dans `tests/test_maze.py`
- [ ] Commit : `feat: implement Maze data structure with wall management`

---

### Étape 4 — `mazegen/maze_generator.py` (4h–6h)
C'est l'étape la plus longue et la plus complexe.

- [ ] Classe `MazeGenerator` avec API publique :
  - `__init__(width, height, seed=None, perfect=True, algorithm="recursive_backtracker")`
  - `generate() -> Maze`
  - `get_maze() -> Maze`
  - `get_solution() -> list[str]`
  - `reset(seed=None)`
- [ ] Implémenter l'algorithme **Recursive Backtracker** :
  1. Partir d'une cellule aléatoire
  2. Marquer comme visitée
  3. Choisir un voisin non visité au hasard, casser le mur, avancer
  4. Si aucun voisin non visité, revenir en arrière (backtrack)
  5. Répéter jusqu'à ce que toutes les cellules soient visitées
- [ ] Utiliser `random.seed(seed)` pour la reproductibilité
- [ ] Placer le motif "42" :
  - Trouver un emplacement valide (assez grand, pas sur ENTRY/EXIT)
  - Fermer tous les murs des cellules du motif
  - Adapter la génération pour contourner ces cellules
  - Si le labyrinthe est trop petit, afficher un warning
- [ ] Vérifier : pas de zone 3×3 ouverte après génération
- [ ] Vérifier : connectivité totale (toutes les cellules accessibles sauf le 42)
- [ ] Si `PERFECT=True` : vérifier qu'il n'y a qu'un seul chemin entre E et S
- [ ] Docstring complète avec exemples d'utilisation (PEP 257)
- [ ] Écrire les tests dans `tests/test_maze_generator.py`
- [ ] Commit : `feat: implement maze generator with recursive backtracker`

---

### Étape 5 — `model/path_finder.py` (1h30)
- [ ] Classe `PathFinder` prenant un `Maze` en paramètre
- [ ] `find_shortest_path(start, end) -> list[str]` : BFS retournant les directions (N, E, S, W)
- [ ] `is_fully_connected(excluded_cells) -> bool` : vérifier que toutes les cellules sont atteignables
- [ ] `is_unique_path(start, end) -> bool` : pour les labyrinthes parfaits, vérifier l'unicité
- [ ] Gérer le cas où aucun chemin n'existe (lever une exception)
- [ ] Écrire les tests dans `tests/test_path_finder.py`
- [ ] Commit : `feat: implement BFS pathfinder with connectivity checks`

---

### Étape 6 — Écriture du fichier de sortie (1h)
- [ ] Fonction ou méthode pour écrire le fichier au format requis :
  - Lignes hexadécimales (une par rangée)
  - Ligne vide
  - Coordonnées ENTRY
  - Coordonnées EXIT
  - Chemin solution en lettres N/E/S/W
- [ ] Toutes les lignes se terminent par `\n`
- [ ] Tester avec le script de validation fourni si disponible
- [ ] Commit : `feat: implement maze output file writer`

---

### Étape 7 — `controller/maze_controller.py` (1h30)
- [ ] Classe `MazeController` qui orchestre tout le flux :
  1. Recevoir le chemin du fichier config
  2. Instancier `ConfigParser` → lire la config
  3. Instancier `MazeGenerator` → générer le labyrinthe
  4. Instancier `PathFinder` → calculer la solution
  5. Écrire le fichier de sortie
  6. Lancer la vue (terminal ou MLX)
- [ ] Gérer les actions utilisateur : régénérer, afficher/masquer solution, changer couleurs
- [ ] Propager les erreurs sous forme de messages clairs (jamais de crash)
- [ ] Commit : `feat: implement maze controller orchestration`

---

### Étape 8 — `a_maze_ing.py` (30 min)
- [ ] Lire `sys.argv` pour récupérer le fichier config
- [ ] Afficher un message d'aide si argument manquant ou `--help`
- [ ] Instancier `MazeController` et appeler la méthode principale
- [ ] Try/except global pour capturer les erreurs et afficher un message propre
- [ ] Commit : `feat: implement main entry point`

---

### Étape 9 — `view/terminal_view.py` (2h–3h)
- [ ] Classe `TerminalView` qui affiche le labyrinthe en ASCII
- [ ] Caractères : `+` pour les coins, `-` pour murs horizontaux, `|` pour murs verticaux
- [ ] Marqueurs pour ENTRY (ex: `E`) et EXIT (ex: `S`)
- [ ] Affichage du chemin solution (ex: `·` ou `*`)
- [ ] Couleurs ANSI pour les murs (modifiables)
- [ ] Couleur optionnelle pour le motif "42"
- [ ] Interactions utilisateur en boucle :
  - `r` → régénérer un nouveau labyrinthe
  - `s` → afficher/masquer la solution
  - `c` → changer les couleurs des murs
  - `q` → quitter
- [ ] Commit : `feat: implement terminal ASCII maze view`

---

### Étape 10 — `view/mlx_view.py` (3h–4h)
- [ ] Classe `MlxView` utilisant MiniLibX pour le rendu graphique
- [ ] Dessiner les murs, passages, entrée, sortie
- [ ] Afficher le chemin solution en surbrillance
- [ ] Gestion des événements clavier : mêmes interactions que terminal
- [ ] Couleurs personnalisables pour murs et motif "42"
- [ ] Commit : `feat: implement graphical maze view with MLX`

---

### Étape 11 — Packaging `mazegen` (1h)
- [ ] Compléter `pyproject.toml` avec les métadonnées du paquet
- [ ] Vérifier que `mazegen/` est importable indépendamment
- [ ] Builder le paquet : `python -m build`
- [ ] Vérifier que le `.whl` et `.tar.gz` sont générés à la racine
- [ ] Tester l'installation dans un venv propre : `pip install mazegen-1.0.0-py3-none-any.whl`
- [ ] Vérifier que `from mazegen import MazeGenerator` fonctionne
- [ ] Commit : `chore: configure mazegen package build`

---

### Étape 12 — Makefile (30 min)
- [ ] Règle `install` : `pip install -r requirements.txt`
- [ ] Règle `run` : `python3 a_maze_ing.py config.txt`
- [ ] Règle `debug` : `python3 -m pdb a_maze_ing.py config.txt`
- [ ] Règle `clean` : supprimer `__pycache__`, `.mypy_cache`, `.pytest_cache`
- [ ] Règle `lint` : `flake8 .` + `mypy` avec les flags du sujet
- [ ] Règle `lint-strict` (optionnel) : `mypy . --strict`
- [ ] Règle `test` : `pytest tests/`
- [ ] Commit : `chore: implement Makefile with required rules`

---

### Étape 13 — README.md (1h30)
- [ ] Première ligne en italique : *This project has been created as part of the 42 curriculum by \<logins\>*
- [ ] Section **Description** : but du projet, fonctionnalités
- [ ] Section **Instructions** : installation, exécution, commandes
- [ ] Section **Configuration** : format complet du fichier config (toutes les clés)
- [ ] Section **Algorithme** : explication du recursive backtracker + pourquoi ce choix
- [ ] Section **Réutilisabilité** : doc du module `mazegen` avec exemples de code
- [ ] Section **Gestion d'équipe** : rôles, planning prévu vs réel, outils utilisés
- [ ] Section **Resources** : liens + description de l'usage de l'IA
- [ ] Commit : `docs: write complete README with all required sections`

---

### Étape 14 — Lint, mypy, tests finaux (1h–2h)
- [ ] Passer `flake8 .` → 0 erreur
- [ ] Passer `mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs` → 0 erreur
- [ ] Passer `pytest tests/ -v` → tous les tests passent
- [ ] Vérifier les type hints sur toutes les fonctions
- [ ] Vérifier les docstrings PEP 257 sur toutes les classes/fonctions
- [ ] Test end-to-end : `python3 a_maze_ing.py config.txt` produit un fichier valide
- [ ] Dernier commit : `chore: final lint, type checks, and test pass`
