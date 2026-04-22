# TODO REMAINING — Ce qui reste à faire pour coller au sujet
> Mise à jour : 22 avril 2026  
> Référence : sujet A-Maze-ing v2.1

---

## PRIORITÉ 1 — Bloquant (obligatoire pour passer la Moulinette / l'évaluation)

### [ ] 1. Ajouter la règle `debug` dans le Makefile

Le sujet (§III.2) exige **obligatoirement** une règle `debug` :
> "Run the main script in debug mode using Python's built-in debugger (e.g., pdb)"

La règle est mentionnée dans le commentaire du Makefile mais n'existe pas.

**À ajouter dans `Makefile` :**
```makefile
debug:
	make install
	. .venv/bin/activate; python3 -m pdb a_maze_ing.py config.txt
```

---

### [ ] 2. Corriger le format des coordonnées dans le fichier de sortie

**Fichier :** `view/menu.py`, méthode `_execute()`

Le sujet précise que la sortie doit contenir les coordonnées sous la forme `0,0` (sans espace).  
Actuellement `str((0, 0)).strip("()")` produit `"0, 0"` (avec espace).

**Fix :**
```python
e = self._controller._config.ENTRY
x = self._controller._config.EXIT
entry = f"{e[0]},{e[1]}"
exit_str = f"{x[0]},{x[1]}"
output += entry + "\n"
output += exit_str + "\n"
```

---

### [ ] 3. Corriger le format du chemin solution dans le fichier de sortie

**Fichier :** `view/menu.py`, méthode `_execute()`

Le code actuel extrait `directions[-1]` depuis le dictionnaire de connexions, ce qui ne produit pas un chemin ordonné valide.

Le sujet précise :
> "The shortest valid path from entry to exit, using the four letters N, E, S, W"

**Fix :** Utiliser la liste ordonnée retournée par `PathFinder._shortest_path()` :
```python
ordered_path = self._controller._finder._shortest_path()
if ordered_path:
    output += ",".join(ordered_path) + "\n"
else:
    output += "\n"
```
*(Vérifier aussi si le séparateur doit être `,` ou espace — comparer avec `output_validator.py`)*

---

### [ ] 4. Implémenter `MazeGenerator.get_solution()`

**Fichier :** `mazegen/maze_generator.py`

L'API publique documentée dans le sujet et dans les docstrings exige `get_solution()`.
Cette méthode doit retourner le chemin solution du labyrinthe généré.

**À ajouter :**
```python
def get_solution(self) -> list[str] | None:
    """Return the solution path as an ordered list of directions.

    Returns:
        List of directions ['N', 'E', ...] or None if no path exists.
    """
    return self.solution_path
```

Et dans `generate()`, calculer et stocker la solution après validation :
```python
from model.path_finder import PathFinder
# ... après validation du labyrinthe ...
# Note: nécessite entry/exit — à passer en paramètre ou via config
```

---

### [ ] 5. Corriger le bug `AttributeError` sur backtracker imperfait

**Fichier :** `mazegen/algorithm.py`

`_get_breakable_walls()` appelle `self._cell_wall_count()`, mais cette méthode est définie uniquement dans `Kruksal`, pas dans `Algorithm`. Tout labyrinthe généré avec backtracker + `PERFECT=False` crash.

**Fix :** Déplacer `_cell_wall_count` dans `Algorithm` :
```python
def _cell_wall_count(self, x: int, y: int) -> int:
    """Return the number of walls surrounding cell (x, y) (0–4)."""
    return self.maze.grid[y][x].bit_count()
```
Et supprimer la copie dans `Kruksal`.

---

## PRIORITÉ 2 — Important (fonctionnel / cohérence)

### [ ] 6. Corriger `MazeGenerator.reset()` — motif 42 non réinitialisé

**Fichier :** `mazegen/maze_generator.py`

Après `reset()`, le motif 42 n'est pas replacé, causant une génération incorrecte.

**Fix :**
```python
def reset(self, seed: int | None = None) -> None:
    if seed is not None:
        self.seed = seed
        random.seed(seed)
    # Réinitialiser la grille via un nouveau Maze
    self.maze = Maze(self.width, self.height)
    self.solution_path = None
    self.tracks = []
    self.forty_two_cells = self.maze.forty_two_cells
```

---

### [ ] 7. Afficher un message clair quand le labyrinthe est trop petit pour le motif 42

**Sujet (§IV.4) :**
> "The '42' pattern may be omitted in case the maze size does not allow it. Print an error message on the console in that case."

Actuellement, `place_42_center()` retourne silencieusement un set vide. Aucun message n'est affiché.

**À ajouter** dans `MazeGenerator.generate()` ou `MazeController.run()` :
```python
if not self.maze.forty_two_cells:
    print("Warning: maze too small to place the '42' pattern.")
```

---

### [ ] 8. Ajouter `ALGORITHM` dans `REQUIRED_KEYS` ou lui donner une valeur par défaut

**Fichier :** `model/config_file.py`

`ALGORITHM: str = Field(...)` est obligatoire pour Pydantic mais absent de `REQUIRED_KEYS`.  
Un config.txt sans `ALGORITHM=` lève une `ValidationError` générique au lieu du message clair habituel.

**Option A** — Rendre optionnel avec valeur par défaut :
```python
ALGORITHM: str = Field(default="backtracker", pattern="^(?i)(backtracker|kruksal)$")
```
Et dans `_parse_optionals`, ajouter `ALGORITHM` avec le défaut `"backtracker"`.

**Option B** — Ajouter `"ALGORITHM"` à `REQUIRED_KEYS` (si obligatoire dans le projet).

---

### [ ] 9. Supprimer le répertoire `path/to/venv/` du dépôt

Ce répertoire est présent à la racine, semble être un vestige d'une ancienne configuration.  
Il ne doit pas être versé dans Git.

```bash
git rm -r path/
echo "path/" >> .gitignore
```

---

### [ ] 10. Remplir `utils/logger.py` ou le supprimer

Le fichier est vide. Le sujet recommande l'utilisation de gestionnaires de logs plutôt que `print()` brut pour les erreurs.

**Option minimale :**
```python
import logging

def get_logger(name: str) -> logging.Logger:
    logging.basicConfig(level=logging.INFO)
    return logging.getLogger(name)
```

Puis l'utiliser dans `maze_generator.py` et `a_maze_ing.py` pour les messages d'erreur.

---

## PRIORITÉ 3 — Qualité / Maintenabilité

### [ ] 11. Corriger le nommage `Cycle_Checker` → `CycleChecker`

- Renommer la classe : `Cycle_Checker` → `CycleChecker` (PEP 8)
- Renommer le fichier : `cycle_cheker.py` → `cycle_checker.py` (faute d'orthographe)
- Mettre à jour tous les imports

---

### [ ] 12. Corriger `encode_hex()` — concaténation en boucle

**Fichier :** `model/maze.py`

```python
# Avant (inefficace O(n²))
hex_string = ""
for row in self.grid:
    for cell in row:
        hex_string += f"{cell:X}"
    hex_string += "\n"

# Après (O(n))
return "\n".join(
    "".join(f"{cell:X}" for cell in row)
    for row in self.grid
) + "\n"
```

---

### [ ] 13. Corriger le re-raise inutile dans `config_file.py`

**Fichier :** `model/config_file.py` (deux occurrences)

```python
# Avant (perd le traceback original)
except ValueError as error:
    raise ValueError(error)

# Après (conserve le traceback)
except ValueError:
    raise
```

---

### [ ] 14. Documenter le `except ValueError: pass` dans `kruksal.py`

**Fichier :** `mazegen/kruksal.py`

```python
try:
    _eligible_walls.remove((nx, ny, opposite_direction))
except ValueError:
    pass  # Ajouter : # Non présent dans la liste — normal, ignoré
```

---

### [ ] 15. Déclarer `_view` et `menu` dans `__init__` de `MazeController`

**Fichier :** `controller/maze_controller.py`

```python
def __init__(self, config_file: str) -> None:
    self._config_file: str = config_file
    self._config: ConfigFile | None = None
    self._generator: MazeGenerator | None = None
    self._cycle_checker: Cycle_Checker | None = None
    self._finder: PathFinder | None = None
    self._view: TerminalView | None = None  # ← manquant
    self.menu: Menu | None = None            # ← manquant
```

---

### [ ] 16. Exposer `Menu._run()` comme méthode publique

**Fichier :** `view/menu.py`

La méthode `_run()` est appelée depuis l'extérieur (`self.menu._run()`). Ajouter une méthode publique :
```python
def run(self) -> None:
    """Public entry point for the menu loop."""
    self._run()
```
Et mettre à jour `MazeController.run()` pour appeler `self.menu.run()`.

---

### [ ] 17. Corriger la docstring de `_no_open_area_around`

**Fichier :** `mazegen/algorithm.py`

La docstring dit "Returns True if there is NO open area" mais la méthode retourne `True` quand elle EN trouve une. Corriger la docstring pour refléter le comportement réel :
```
Returns True if a forbidden 3x3 open area is found around (x, y),
False if the area is clear.
```

---

### [ ] 18. Remplacer la double vérification `mimetypes` par un simple `endswith`

**Fichier :** `model/config_file.py`

```python
# Avant
from mimetypes import guess_type
if self.OUTPUT_FILE.lower().endswith(".txt") \
        and guess_type(self.OUTPUT_FILE)[0] == "text/plain":
    return self

# Après
if self.OUTPUT_FILE.lower().endswith(".txt"):
    return self
```
Supprimer l'import `mimetypes`.

---

### [ ] 19. Corriger les `except Exception:` trop larges dans `terminal_spawn_runner.py`

**Fichier :** `view/terminal_spawn_runner.py`

```python
# Avant
except Exception:
    ...

# Après — attraper OSError, ValueError, etc. selon le contexte
except (OSError, ValueError, RuntimeError):
    ...
```

---

### [ ] 20. Compléter les tests manquants

- [ ] Ajouter des tests pour `CycleChecker` (après renommage)
- [ ] Tester le backtracker en mode imperfait (révèle BUG 2)
- [ ] Tester l'intégration complète : générer → écrire fichier → valider avec `output_validator.py`
- [ ] Corriger `test_path_finder.py` : les tests appellent `_shortest_path()` comme si elle retournait `dict`, mais elle retourne `list[str] | None`
- [ ] Tester le cas "labyrinthe trop petit pour le motif 42" (message affiché)
- [ ] Ajouter un test de `MazeGenerator.reset()` après correction du BUG 6

---

## PRIORITÉ 4 — Bonus (non obligatoire mais valorisé)

### [ ] 21. Implémenter la vue ncurses (`curse_view.py`)

Mentionnée dans le README comme alternative de vue mais non implémentée. Le sujet accepte terminal ou graphique — la vue terminal actuelle suffit, mais la vue ncurses serait un bonus.

### [ ] 22. Ajouter une règle `make package` pour builder le `.whl`

Le sujet (§VI) demande que le paquet `mazegen` soit installable via pip.  
Ajouter dans le Makefile :
```makefile
package:
	make install
	. .venv/bin/activate; python3 -m build
```

### [ ] 23. Utiliser le `utils/logger.py` partout (remplacement des `print` d'erreur)

Remplacer les `print("Error: ...")` dans `maze_generator.py`, `a_maze_ing.py` par des appels au logger.

### [ ] 24. Implémenter la vue MLX graphique (`mlx_view.py`)

Mentionnée dans le README comme "en cours". Non obligatoire si la vue terminal fonctionne.

---

## Résumé des fichiers à modifier

| Fichier | Actions requises |
|---|---|
| `Makefile` | Ajouter règle `debug:` |
| `view/menu.py` | BUG 1 (coordonnées), BUG 7 (chemin solution) |
| `mazegen/maze_generator.py` | Implémenter `get_solution()`, corriger `reset()` |
| `mazegen/algorithm.py` | Déplacer `_cell_wall_count`, corriger docstring |
| `mazegen/kruksal.py` | Supprimer copie de `_cell_wall_count`, documenter `except` |
| `model/config_file.py` | Fix `ALGORITHM`, supprimer re-raise inutile, supprimer `mimetypes` |
| `controller/maze_controller.py` | Déclarer `_view` et `menu` dans `__init__`, appeler `menu.run()` |
| `view/menu.py` | Ajouter `Menu.run()` public |
| `model/cycle_cheker.py` | Renommer fichier + classe |
| `view/terminal_spawn_runner.py` | Réduire largeur des `except Exception` |
| `utils/logger.py` | Implémenter ou supprimer |
| `model/maze.py` | Corriger `encode_hex()` |
| Partout | Message d'avertissement quand motif 42 impossible |
