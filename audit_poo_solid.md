# Audit POO & SOLID — A-Maze-ing — Mise à jour 11/04/2026 (v7)

> Révision complète v7 : re-vérification de chaque point sur la codebase actuelle,
> mise à jour des statuts, correction des points déjà résolus, ajout des nouveaux tests.
> Auteurs : **gacattan**, **cyakisan**

---

## 1. Bilan POO

### ✅ Points positifs

| Principe | Élément | Détail |
|----------|---------|--------|
| Héritage | `Algorithm` → `Backtracker`, `Kruksal` | Hiérarchie propre avec classe abstraite ABC |
| Abstraction | `Algorithm.generate()` | Méthode abstraite force l'implémentation dans chaque sous-classe |
| Séparation | `Maze` / `MazeValidator` | Validation déléguée, modèle allégé |
| Architecture MVC | Dossiers `model/`, `view/`, `controller/` | Structure claire et respectée |
| Docstrings / type hints | Méthodes publiques | Conformes PEP 257, présents sur les API exposées |
| Constante bien placée | `PATTERN_42` dans `Maze` | Données du motif au niveau du modèle |
| Utilitaires centralisés | `_get_neighbors_of_cell()`, `_get_direction_neighbor()`, `_get_maze_boundaries()` dans `Algorithm` | Logique algo dans la bonne classe |
| Code mort supprimé | `config_parser.py`, `_get_42_neighbors()`, stubs vides | Pas de doublon |
| PathFinder simplifié | `find_k_shortest_paths()` | Retourne `list[dict]` directement |
| LSP respecté | `Backtracker.generate()` | Retourne `list[tuple[int,int,str]]` identique à Kruskal |
| Rendu unifié | `TerminalView._render()` + `play()` | Plus de duplication |
| Attribut `perfect` | `Backtracker.perfect = True`, `Kruksal.perfect = False` | Chaque algo porte son flag |
| `_second_loop` privé ✅ | `Kruksal._second_loop()` | Méthode de classe correctement préfixée `_` |
| Contrôleur décomposé | `_load_config()`, `_create_gen()`, `_create_pathfinder()`, `_create_view()` | `run()` délègue proprement |
| Config validée pydantic | `ConfigFile` (pydantic BaseModel) | Validation ENTRY/EXIT/dimensions centralisée |

### ⚠️ À corriger — POO

#### 1. `get_solution()` morte dans `MazeGenerator`
`self.solution_path` n'est **jamais alimenté** — la méthode lève toujours `ValueError`.
Le contrôleur contourne via `PathFinder` directement.
**Recommandation** : supprimer `get_solution()` et `self.solution_path`.

#### 2. Attributs publics de `Maze` (`grid`, `width`, `height`)
Accédés directement depuis toutes les couches.
**Recommandation** : `width` et `height` en `@property` read-only ; `grid` protégé.

#### 3. `self.menu` est public dans `MazeController`
Devrait être `self._menu`.

#### 4. DIRECTIONS dict dupliqué × 2
`PathFinder.DIRECTIONS` et `Maze._DIRECTIONS` : **même dictionnaire, 2 endroits**.
(`Algorithm` utilise désormais `self.maze._DIRECTIONS` — l'une des 3 copies a été éliminée ✅)
**Recommandation** : définir une fois dans `model/maze.py` et importer dans `PathFinder`.

#### 5. `place_42_center()` appelle `self.forty_two_cells.add()` avant l'assignation
Le pattern `self.forty_two_cells = set()` suivi de `self.forty_two_cells = self.place_42_center()`
est fragile : `place_42_center` accumule dans `self.forty_two_cells` ET le retourne.
**Recommandation** : utiliser un set local dans `place_42_center()` et le retourner.

---

## 2. Bilan SOLID

### S — Single Responsibility

| Classe | SRP respecté ? | Note |
|--------|---------------|------|
| `Maze` | ⚠️ | Données + placement 42 + helpers navigation — légèrement surchargé |
| `MazeValidator` | ✅ | Responsabilité unique : valider |
| `ConfigFile` | ✅ | Données config + parsing statique — pydantic gère la validation |
| `PathFinder` | ✅ | Responsabilité unique : trouver le chemin |
| `Algorithm` | ✅ | Contrat abstrait + utilitaires centralisés |
| `Backtracker` | ✅ | Un seul algorithme, propre |
| `Kruksal` | ✅ | `_second_loop` extrait — logique claire |
| `MazeGenerator` | ⚠️ | Factory + seed + validation + `get_solution()` morte (jamais alimentée) |
| `MazeController` | ⚠️ | `run()` délègue bien via sous-méthodes, mais output fichier absent |
| `TerminalView` | ✅ | `play()` unifié, `_render()` unique |

### O — Open/Closed

| Élément | État | Problème |
|---------|------|---------|
| Ajout d'un algorithme | ✅ | Sous-classe + attribut `perfect` suffisent — `_build_algorithm()` itère sur `self.algorithms` |
| Ajout d'une vue | ❌ | `MazeController` instancie `TerminalView` en dur |
| `_build_algorithm()` | ⚠️ | `for/else` Python ambigu — le `else` s'exécute si la boucle se termine sans `return` (cas d'erreur) |

### L — Liskov Substitution ✅

`Backtracker.generate()` et `Kruksal.generate()` retournent tous deux `list[tuple[int, int, str]]`.
Aucun `isinstance` dans le contrôleur.

### I — Interface Segregation ⚠️

`MazeController` dépend de `TerminalView` concrète. Aucune interface commune avec `MlxView`.
**Recommandation** :
```python
# view/abstract_view.py
from abc import ABC, abstractmethod

class AbstractView(ABC):
    @abstractmethod
    def play(self, tracks: list) -> None: ...
    @abstractmethod
    def show_solution(self, paths: list, is_perfect: bool, tracks: list) -> None: ...
```

### D — Dependency Inversion ⚠️

| Dépendance | Problème |
|-----------|---------|
| `MazeController` → `TerminalView` | Module haut niveau dépend d'un détail concret |
| `TerminalView` → `Maze.grid` | Accès direct aux attributs internes |
| `Algorithm` → `Maze` | Acceptable (même package) |
| `Kruksal` → `MazeValidator` | Acceptable (même couche) |

---

## 3. Notes par module

| Module | Note /5 | Résumé |
|--------|---------|--------|
| `model/maze.py` | **4/5** | `_DIRECTIONS` centralisé ✅ — `place_42_center()` mélange effet de bord et retour, `forty_two_cells` pré-init fragile |
| `model/maze_validator.py` | **4.5/5** | SRP excellent, BFS correct, bien documenté |
| `model/config_file.py` | **4/5** | Pydantic bien utilisé — validation clé `VIEW` résiduelle sans correspondance dans REQUIRED/OPTIONAL_KEYS |
| `model/path_finder.py` | **4.5/5** | BFS optimisé, élagage `exit_dist`, `find_k_shortest_paths()` propre |
| `mazegen/algorithm.py` | **4.5/5** | Utilitaires centralisés ✅ — utilise `self.maze._DIRECTIONS` (plus de copie locale) |
| `mazegen/backtracker.py` | **5/5** | Propre, LSP respecté, `perfect = True` |
| `mazegen/kruksal.py` | **4/5** | `_second_loop` correctement privé ✅ — `_breakable_walls` non typé (`maze`, `x`, `y`), ligne conditions >100 chars |
| `mazegen/maze_generator.py` | **3/5** | `get_solution()` morte (jamais alimentée), `reset()` réinitialise la grille à la main, header docstring obsolète |
| `controller/maze_controller.py` | **3.5/5** | Décomposé ✅ — output fichier absent, `self.menu` public, `_create_gen/pathfinder/view` sans `-> None` |
| `view/terminal_view.py` | **4.5/5** | Rendu unifié ✅ — pas d'`AbstractView`, `encode_hex` concaténation O(n²) |
| `view/menu.py` | **4/5** | Clair — `_settings()` très long, validation saisie via `click` mais sans retour typé |
| `view/mlx_view.py` | **0/5** | Stub total (bonus) |
| `tests/test_maze.py` | **4/5** | 32 tests — bonne couverture structure Maze |
| `tests/test_maze_generator.py` | **4/5** | 26 tests — génération, déterminisme, reset, petits labyrinthes |
| `tests/test_path_finder.py` | **4/5** | 22 tests ✅ (stub remplacé) — couloirs, k-chemins, inaccessible, connexions |
| `tests/test_config_parser.py` | **4/5** | 22 tests — bonne couverture `ConfigFile.parse()` |
| `tests/test_maze_validator.py` | **4.5/5** | 31 tests ✅ (nouveau fichier) — toutes les règles de validation couvertes |
| `Makefile` | **0/5** | Stub total — 🔴 OBLIGATOIRE |

---

## 4. Note globale

| Catégorie | Note |
|-----------|------|
| Architecture générale / MVC | 16/20 |
| Respect POO (encapsulation, héritage, polymorphisme) | 17/20 |
| Respect SOLID | 15/20 |
| Complétude fonctionnelle (sujet) | 15/20 |
| Qualité des tests | 15/20 |
| **Note globale estimée** | **16/20** |

> **Évolution** : +1 point vs v6 grâce à l'ajout de `test_path_finder.py` (22 tests)
> et `test_maze_validator.py` (31 tests) — total 138 tests, 0 en échec.

---

## 5. Code refactorisable & optimisations

### 5.1 Duplications à éliminer

| Problème | Localisation | Solution |
|----------|-------------|---------|
| `DIRECTIONS` dict défini 2× | `Maze._DIRECTIONS`, `PathFinder.DIRECTIONS` | Définir dans `Maze`, importer dans `PathFinder` |
| `_get_neighbors_of_cell()` dans `Maze` et `Algorithm` | `model/maze.py`, `mazegen/algorithm.py` | Conserver uniquement dans `Algorithm`, supprimer de `Maze` |
| `_get_direction_neighbor()` dans `Maze` et `Algorithm` | idem | Idem |
| `_get_maze_boundaries()` dans `Maze` et `Algorithm` | idem | Idem |

### 5.2 Simplifications de code

```python
# maze.py — _is_42_wall : if/else inutile
# Avant :
def _is_42_wall(self, x, y, wall_direction) -> bool:
    if self._get_direction_neighbor(x, y, wall_direction) not in self.forty_two_cells:
        return False
    else:
        return True

# Après :
def _is_42_wall(self, x, y, wall_direction) -> bool:
    return self._get_direction_neighbor(x, y, wall_direction) in self.forty_two_cells
```

```python
# maze.py — place_42_center : effet de bord + retour couplés
# Avant :
self.forty_two_cells: set[tuple[int, int]] = set()
self.forty_two_cells = self.place_42_center()  # méthode mutate ET retourne

# Après :
def place_42_center(self) -> set[tuple[int, int]]:
    result: set[tuple[int, int]] = set()
    ...
    result.add((x, y))
    ...
    return result
```

```python
# maze.py — encode_hex : concaténation en boucle (O(n²))
# Avant :
hex_string = ""
for row in self.grid:
    for cell in row:
        hex_string += f"{cell:X}"
    hex_string += "\n"

# Après :
return "\n".join("".join(f"{cell:X}" for cell in row) for row in self.grid) + "\n"
```

```python
# maze_validator.py — _validate_cell_values : boucle manuelle
# Avant :
for row in self._maze.grid:
    for cell in row:
        if not (0 <= cell <= 15):
            return False
return True

# Après :
return all(0 <= cell <= 15 for row in self._maze.grid for cell in row)
```

```python
# mazegen/maze_generator.py — reset() : réinitialisation manuelle fragile
# Avant :
for i in range(len(self.maze.grid)):
    for j in range(len(self.maze.grid[i])):
        self.maze.grid[i][j] = 15

# Après :
self.maze = Maze(self.width, self.height)
```

### 5.3 Code mort à supprimer

| Élément | Fichier | Action |
|---------|---------|--------|
| `get_solution()` + `self.solution_path` | `mazegen/maze_generator.py` | Supprimer — jamais alimenté |
| Validation clé `VIEW` dans `_parse_line` | `model/config_file.py` | Supprimer — clé non déclarée dans REQUIRED/OPTIONAL_KEYS |
| Header docstring `algorithm` param | `mazegen/maze_generator.py` | Mettre à jour |

### 5.4 Annotations manquantes

| Méthode | Fichier | Annotation manquante |
|---------|---------|---------------------|
| `_create_gen()` | `controller/maze_controller.py` | `-> None` |
| `_create_pathfinder()` | `controller/maze_controller.py` | `-> None` |
| `_create_view()` | `controller/maze_controller.py` | `-> None` |
| `_second_loop()` | `mazegen/kruksal.py` | Retourne `tuple[Maze, list]` — partiellement typé |
| `_breakable_walls()` | `mazegen/kruksal.py` | Paramètres `maze`, `x`, `y` non typés |

---

## 6. Actions prioritaires restantes

| Priorité | Action | Fichier(s) |
|----------|--------|-----------|
| ✅ FAIT | `PathFinder` BFS + k chemins | `model/path_finder.py` |
| ✅ FAIT | Intégrer `PathFinder` dans le contrôleur | `controller/maze_controller.py` |
| ✅ FAIT | Affichage solution + navigation N/P/Q/S/C | `view/terminal_view.py` |
| ✅ FAIT | LSP corrigé — `Backtracker` retourne `list[tuple[int,int,str]]` | `mazegen/backtracker.py` |
| ✅ FAIT | `_render()` + `play()` unifiés | `view/terminal_view.py` |
| ✅ FAIT | `config_parser.py` supprimé — `ConfigFile` seul point d'entrée | `model/` |
| ✅ FAIT | `_second_loop` extrait en méthode privée | `mazegen/kruksal.py` |
| ✅ FAIT | Contrôleur décomposé en sous-méthodes | `controller/maze_controller.py` |
| ✅ FAIT | Code mort nettoyé (`_get_42_neighbors`, `__main__`, stubs) | divers |
| ✅ FAIT | `tests/test_path_finder.py` — 22 tests implémentés | `tests/test_path_finder.py` |
| ✅ FAIT | `tests/test_maze_validator.py` — 31 tests créés | `tests/test_maze_validator.py` |
| 🔴 CRITIQUE | Créer le `Makefile` (install, run, debug, clean, lint, test) | `Makefile` |
| 🔴 CRITIQUE | Écrire le fichier de sortie (grille hex + ligne vide + ENTRY + EXIT + chemin) | `controller/maze_controller.py` |
| 🟠 IMPORTANT | Supprimer `get_solution()` + `self.solution_path` (jamais alimentés) | `mazegen/maze_generator.py` |
| 🟠 IMPORTANT | Créer `AbstractView` et l'injecter dans `MazeController` | `view/`, `controller/` |
| 🟡 Refactoring | Dédupliquer le dict DIRECTIONS (`Maze` → `PathFinder`) | `model/path_finder.py` |
| 🟡 Refactoring | Simplifier `_is_42_wall`, `encode_hex`, `_validate_cell_values`, `reset()` | voir §5.2 |
| 🟡 Refactoring | Refactoriser `place_42_center()` avec set local (plus d'effet de bord) | `model/maze.py` |
| 🟡 Refactoring | Supprimer `self.menu` → `self._menu` dans `MazeController` | `controller/maze_controller.py` |
| 🟡 Refactoring | Ajouter `-> None` sur `_create_gen/pathfinder/view` | `controller/maze_controller.py` |
| 🟡 Refactoring | Typer `_second_loop` et `_breakable_walls` complètement | `mazegen/kruksal.py` |
| 🟡 Refactoring | Supprimer validation clé `VIEW` résiduelle | `model/config_file.py` |
