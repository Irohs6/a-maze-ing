# FEEDBACK — Audit complet du projet A-Maze-ing
> Généré le 22 avril 2026

---

## 1. Vue d'ensemble

| Critère | État | Note |
|---|---|---|
| Conformité au sujet (obligatoire) | ⚠️ Partiel | Voir §3 |
| Qualité du code | ⚠️ Moyen | Plusieurs bugs réels |
| Gestion des exceptions | ⚠️ Insuffisant | Voir §5 |
| Type annotations & mypy | ⚠️ Partiel | Quelques manques |
| Docstrings | ✅ Bon | Présentes et utiles |
| Tests | ✅ Bon | Bonne couverture fonctionnelle |
| Architecture MVC | ✅ Bon | Structure propre |
| Makefile | ⚠️ Incomplet | Règle `debug` manquante |
| README | ✅ Bon | Complet et bien structuré |
| .gitignore | ✅ Présent | |

---

## 2. Bugs réels (bloquants ou critiques)

### BUG 1 — Format de sortie : coordonnées avec espace
**Fichier :** `view/menu.py`, méthode `_execute()`

```python
entry, exit = (
    str(self._controller._config.ENTRY).strip("()"),
    str(self._controller._config.EXIT).strip("()"),
)
```

`str((0, 0))` vaut `"(0, 0)"`, et `.strip("()")` donne `"0, 0"` (avec une espace après la virgule).  
Le sujet exige le format `0,0` (sans espace). Le validateur automatique (Moulinette) échouera sur ce point.

**Fix :** Utiliser `f"{x},{y}"` ou `",".join(map(str, self._controller._config.ENTRY))`.

---

### BUG 2 — `_cell_wall_count` non définie dans `Algorithm` mais appelée par `second_loop()`
**Fichier :** `mazegen/algorithm.py`, `_get_breakable_walls()`

La méthode `_cell_wall_count` est définie uniquement dans `Kruksal`, mais `_get_breakable_walls()` est une méthode de la classe `Algorithm`, héritée par `Backtracker`. Quand `Backtracker` génère un labyrinthe **imperfait** (`PERFECT=False`), `second_loop()` est appelée, qui appelle `_get_breakable_walls()`, qui appelle `self._cell_wall_count()` — méthode que `Backtracker` n'a pas.

Résultat : **`AttributeError` garanti** pour tout labyrinthe backtracker imperfait.

**Fix :** Déplacer `_cell_wall_count` dans la classe `Algorithm`.

---

### BUG 3 — `_no_open_area_around` : nom/docstring inversés
**Fichier :** `mazegen/algorithm.py`

```python
def _no_open_area_around(self, original_x, original_y) -> bool:
    """Returns True if there is NO fully open 3x3 block ..."""
    ...
    if validator._is_3x3_open(...):
        return True  # ← retourne True quand une zone est trouvée
    return False
```

La docstring dit "Retourne True s'il n'y a PAS de zone ouverte", mais le code retourne True quand il EN trouve une. L'appelant dans `second_loop()` fait :

```python
if self._no_open_area_around(x, y):
    self.maze.add_wall(x, y, wall_direction)
```

Le comportement final est accidentellement correct (le mur est remis quand une zone ouverte est détectée), mais la logique est trompeuse et un futur mainteneur pourrait introduire un vrai bug en se fiant à la docstring.

---

### BUG 4 — `MazeGenerator.get_solution()` absente
**Fichier :** `mazegen/maze_generator.py`

La méthode `get_solution()` est mentionnée dans :
- Le docstring de la classe (`get_solution() : retourne le chemin solution`)
- L'exemple d'usage dans le docstring (`solution_path = generator.get_solution()`)
- Le README  
- Le sujet (API publique du paquet mazegen)

Mais elle **n'est pas implémentée**. `solution_path` est stocké à `None` et jamais renseigné.

---

### BUG 5 — `ConfigFile.ALGORITHM` requis Pydantic mais absent de `REQUIRED_KEYS`
**Fichier :** `model/config_file.py`

```python
ALGORITHM: str = Field(..., pattern="^(?i)(backtracker|kruksal)$")
```

Le `Field(...)` signifie que ce champ est obligatoire pour Pydantic. Si l'utilisateur oublie `ALGORITHM=` dans son config.txt, Pydantic lève une `ValidationError` avec un message d'erreur générique, au lieu du message clair `KeyError('ALGORITHM has not properly been defined in the config.txt file')`.

De plus, si l'utilisateur met un algorithme valide dans le config le champ marche, mais la validation côté `_validate_required_keys()` ne le vérifie pas, créant une incohérence dans la chaîne de validation.

---

### BUG 6 — `MazeGenerator.reset()` ne réinitialise pas le motif 42
**Fichier :** `mazegen/maze_generator.py`

```python
def reset(self, seed: int | None = None) -> None:
    ...
    for i in range(len(self.maze.grid)):
        for j in range(len(self.maze.grid[i])):
            self.maze.grid[i][j] = 15
    self.solution_path = None
    self.tracks = []
    self.forty_two_cells = set()
```

`reset()` remet toutes les cellules à 15 manuellement mais ne rappelle pas `place_42_center()`. Après un `reset()`, `maze.forty_two_cells` est vide, donc la prochaine génération ne protège plus les cellules du motif 42.

---

### BUG 7 — Format du chemin solution dans le fichier de sortie
**Fichier :** `view/menu.py`, méthode `_execute()`

```python
for directions in paths[0].values():
    output += directions[-1]
output = output[:-1]
output += "\n"
```

`paths[0]` est un `dict[tuple[int, int], list[str]]` (dictionnaire de connexions par cellule). Prendre `directions[-1]` pour chaque cellule retourne la **dernière direction dans la liste de connexions**, pas le chemin ordonné N/E/S/W. L'ordre d'itération d'un dict en Python 3.7+ est l'ordre d'insertion, mais les valeurs de direction sont des listes non ordonnées représentant les connexions (entrée et sortie). Ce code ne produit pas un chemin valide.

Le sujet précise : "The shortest valid path from entry to exit, using the four letters N, E, S, W". Il faut utiliser la liste ordonnée de directions retournée par `PathFinder._shortest_path()`.

---

## 3. Conformité au sujet

### ✅ Points conformes

- Génération aléatoire avec reproductibilité via seed ✅
- Fichier de configuration avec format KEY=VALUE ✅
- Clés obligatoires : WIDTH, HEIGHT, ENTRY, EXIT, OUTPUT_FILE, PERFECT ✅
- Labyrinthe parfait (un seul chemin) implémenté via backtracker ✅
- Labyrinthe imparfait (Kruskal modifié) ✅
- Motif "42" centré obligatoire ✅
- Zones 3×3 interdites détectées ✅
- Validation complète (connectivité, symétrie des murs, bordures) ✅
- Représentation visuelle terminal avec animation ✅
- Encodage hexadécimal 4 bits (N/E/S/W) ✅
- Entrée et sortie dans le fichier de sortie ✅ (mais voir BUG 1)
- Architecture MVC ✅
- Paquet `mazegen` importable ✅
- Makefile : `install`, `run`, `clean`, `lint`, `lint-strict`, `test` ✅
- README complet ✅
- .gitignore ✅
- `pyproject.toml` avec mypy + flake8 + pytest configurés ✅
- Docstrings PEP 257 généralisées ✅
- Type hints sur toutes les fonctions ✅ (quasi-complètes)

### ❌ Non-conformités / Manques

| Point obligatoire | Problème |
|---|---|
| Règle `debug` dans le Makefile | Présente en commentaire **mais absente comme vraie règle** (`debug:` manquant) |
| Chemin solution dans le fichier de sortie | Format incorrect (voir BUG 7) |
| Coordonnées entry/exit dans le fichier | Espace parasite dans le format (voir BUG 1) |
| `get_solution()` dans l'API publique `mazegen` | Non implémentée (voir BUG 4) |
| Message d'erreur quand 42 est impossible | Pas de message clair affiché à l'utilisateur quand le labyrinthe est trop petit |

### ⚠️ Optionnel/Bonus non implémentés

| Feature | État |
|---|---|
| Vue graphique MLX | Non implémentée (mentionnée dans README comme "en cours") |
| Vue ncurses (`curse_view.py`) | Non implémentée (mentionnée dans README) |
| Build du paquet `.whl` (distribution) | Aucune règle `make package` / `make build` |
| Mode `PLAYABLE` | Configuré (ConfigFile) mais jamais utilisé dans le controller/view |

---

## 4. Qualité du code

### Nommage non conforme PEP 8
- `Cycle_Checker` → devrait être `CycleChecker`
- `cycle_cheker.py` → faute d'orthographe dans le nom de fichier (`cheker` au lieu de `checker`)

### Code dupliqué
- `_DIRECTIONS` est défini dans `Maze` comme attribut de classe. C'est bien. Mais du code y accède via `self.maze._DIRECTIONS` (attribut privé d'une autre classe). Il faudrait l'exposer en attribut public ou le sortir dans un module `constants.py`.
- `REVERSE` est défini à la fois dans `PathFinder` et dans `Kruksal`, identiques.

### `encode_hex` inefficace
**Fichier :** `model/maze.py`
```python
def encode_hex(self) -> str:
    hex_string = ""
    for row in self.grid:
        for cell in row:
            hex_string += f"{cell:X}"  # concaténation en boucle
        hex_string += "\n"
    return hex_string
```
La concaténation de strings en boucle est O(n²). Utiliser `"".join(...)`.

### `_is_42_wall` verbose et lisibilité inversée
**Fichier :** `mazegen/algorithm.py`
```python
def _is_42_wall(self, x, y, wall_direction) -> bool:
    if (...) not in self.forty_two_cells and (x, y) not in self.forty_two_cells:
        return False
    else:
        return True
```
Simplifiable en `return ... in self.forty_two_cells or (x, y) in self.forty_two_cells`.

### Accès à membre privé depuis l'extérieur
**Fichier :** `controller/maze_controller.py`
```python
self.menu._run()
```
`_run()` est un membre privé de `Menu` appelé depuis le controller. La convention est d'exposer une méthode publique `run()`.

### `_view` non typé dans `MazeController`
**Fichier :** `controller/maze_controller.py`
`_view` est créé dynamiquement dans `_create_view()` sans être initialisé dans `__init__`. Si `_create_view()` n'est pas appelé, `self._view` n'existe pas → `AttributeError`. Même problème pour `menu`.

### `utils/logger.py` vide
Le fichier existe, est dans le `.gitignore`... mais est vide. Il n'est utilisé nulle part. Les erreurs sont toutes affichées avec `print()` brut.

### `path/to/venv/` dans le dépôt
Un répertoire `path/to/venv/` est présent à la racine du projet. C'est un vestige de configuration, probablement non intentionnel. Il doit être supprimé.

### `output_validator.py` : `open()` sans gestionnaire de contexte
```python
for line in open(sys.argv[1]):
```
Le fichier n'est jamais fermé explicitement. Utiliser `with open(...) as f:`.

### `mimetypes.guess_type` pour valider l'extension `.txt`
**Fichier :** `model/config_file.py`
```python
if (
    self.OUTPUT_FILE.lower().endswith(".txt")
    and guess_type(self.OUTPUT_FILE)[0] == "text/plain"
):
```
La double vérification est redondante : si le fichier termine en `.txt`, `guess_type()` retournera toujours `text/plain`. La vérification `endswith(".txt")` seule suffit. L'import `mimetypes` est inutile.

---

## 5. Gestion des exceptions (try/except)

### `except Exception:` trop large (silencieux)
**Fichier :** `view/terminal_spawn_runner.py`
```python
except Exception:
    import traceback
    traceback.print_exc()
    input("Press Enter to exit...")
    return
```
Attrape `SystemExit` et `KeyboardInterrupt` en plus des vraies erreurs. Utiliser `except (ValueError, TypeError, RuntimeError)` ou attraper des types spécifiques.

### Re-raise inutile dans `config_file.py`
```python
except ValueError as error:
    raise ValueError(error)  # perd le traceback original
```
Ce pattern apparaît deux fois (`_parse_types` et `_parse_optionals`). Il est équivalent à `raise` sans argument mais perd le traceback original. Utiliser simplement `raise` se seul.

### `except ValueError: pass` sans commentaire
**Fichier :** `mazegen/kruksal.py`
```python
try:
    _eligible_walls.remove((nx, ny, opposite_direction))
except ValueError:
    pass
```
Intentionnel (suppression d'un élément inexistant dans une liste), mais sans commentaire explicatif. Un futur mainteneur pourrait le supprimer croyant que c'est un oubli.

### `except FileNotFoundError: return False` silencieux
**Fichier :** `view/terminal_launcher.py`
L'échec du lancement de la fenêtre terminal est silencieux — pas de log, pas de message. En mode de fallback c'est acceptable, mais un log `DEBUG` serait utile.

### `except OSError: pass` dans `terminal_spawn_runner.py`
**Fichier :** `view/terminal_spawn_runner.py:41`
```python
except OSError:
    pass
```
Silencieux sans explication. Même recommandation que ci-dessus.

---

## 6. Type annotations & mypy

| Fichier | Problème |
|---|---|
| `controller/maze_controller.py` | `_view` non déclaré dans `__init__`, non typé |
| `controller/maze_controller.py` | `menu` non déclaré et non typé dans `__init__` |
| `mazegen/maze_generator.py` | `solution_path: list[Any]` trop générique ; devrait être `list[str]` |
| `model/config_file.py` | `ALGORITHM` est required mais absent de `REQUIRED_KEYS` — confusion pour mypy |
| `mazegen/algorithm.py` | `perfect: ClassVar[bool]` absent — `is_perfect` est un attribut d'instance mais pas de classe abstraite |

---

## 7. Tests

### Points forts
- Couverture correcte de `Maze`, `MazeValidator`, `ConfigFile`, `PathFinder`
- Tests paramétrés pour les clés manquantes
- Fixtures réutilisables

### Lacunes
- `test_path_finder.py` : appelle `pf_corridor._shortest_path()` mais cette méthode retourne `list[str] | None`, pas `dict[tuple, list[str]]` comme prévu dans les assertions. Les tests sont incorrects (basés sur `find()`, pas `_shortest_path()`).
- Aucun test de `CycleChecker`
- Aucun test d'intégration du fichier de sortie (contenu final vérifié vs le validateur `output_validator.py`)
- Aucun test de `Menu` ou du flux complet contrôleur
- Aucun test sur les labyrinthes imperfaits avec backtracker (ce qui révèlerait le BUG 2)

---

## 8. Récapitulatif des priorités

### Critique (bloquant pour la notation)
1. ❌ Règle `debug` manquante dans le Makefile
2. ❌ Format coordonnées avec espace (BUG 1) — échoue la Moulinette
3. ❌ Format chemin solution incorrect (BUG 7) — échoue la Moulinette
4. ❌ `get_solution()` non implémentée dans `MazeGenerator` (BUG 4)
5. ❌ `AttributeError` sur backtracker imperfait (BUG 2)

### Important (impact fonctionnel)
6. ⚠️ `reset()` ne réinitialise pas le motif 42 (BUG 6)
7. ⚠️ `ALGORITHM` manquant en config donne une erreur Pydantic générique (BUG 5)
8. ⚠️ `utils/logger.py` vide — pas de logging
9. ⚠️ `path/to/venv/` à supprimer du repo

### Améliorable (qualité, maintenabilité)
10. `encode_hex` → utiliser `"".join()`
11. `_cell_wall_count` → déplacer dans `Algorithm`
12. `CycleChecker` → nommage PEP 8 + faute d'orthographe dans le nom de fichier
13. `_no_open_area_around` → docstring/nom inversé
14. `except ValueError: raise ValueError(error)` → remplacer par `raise`
15. Exposer `Menu.run()` comme méthode publique
16. Déclarer `_view` et `menu` dans `__init__` de `MazeController`
17. Supprimer l'import `mimetypes` inutilement complexe
