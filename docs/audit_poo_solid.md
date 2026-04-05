# Audit POO & SOLID — A-Maze-ing — Mise à jour 05/04/2026

> Révision intégrant le refactoring terminal_view, la correction LSP, l'implémentation PathFinder et l'unification des algorithmes.
> Auteurs : **gacattan**, **cyakisan**

---

## 1. Bilan POO

### ✅ Points positifs

| Principe | Élément | Détail |
|----------|---------|--------|
| Encapsulation | `ConfigParser.__config` | Name mangling (`__config`) — données internes protégées |
| Héritage | `Algorithm` → `Backtracker`, `Kruksal` | Hiérarchie propre avec classe abstraite ABC |
| Abstraction | `Algorithm.generate()` | Méthode abstraite force l'implémentation dans chaque sous-classe |
| Séparation | `Maze` / `MazeValidator` | Validation déléguée, modèle allégé |
| Architecture MVC | Dossiers `model/`, `view/`, `controller/` | Structure claire et respectée |
| Docstrings / type hints | Méthodes publiques | Conformes PEP 257, présents sur les API exposées |
| Méthode partagée | `place_42_center()` dans `Algorithm` | Logique commune centralisée dans la classe parent |
| ~~LSP~~ **FIXED** | `Backtracker.generate()` | Retourne désormais `list[tuple[int,int,str]]` identique à Kruskal |
| Rendu unifié | `TerminalView._render()` | `_print_with_cursor` + `print_unicode` fusionnés, plus de duplication |
| Animation unifiée | `TerminalView.play()` | `play()` + `play_kruksal()` fusionnés, format commun |

### ⚠️ À corriger — POO

#### 1. `PATTERN_42` stocké dans `Maze` (mauvaise couche)
`Maze.__init__` définit `self.PATTERN_42` — un motif visuel de génération.  
La structure de données du labyrinthe n'a pas à connaître ce motif.  
**Recommandation** : déplacer `PATTERN_42` comme constante de classe dans `Algorithm` ou dans un fichier de constantes séparé.

```python
# Avant (dans Maze.__init__)
self.PATTERN_42 = [[15, 0, 15, ...], ...]

# Après (dans Algorithm, comme constante de classe)
class Algorithm(ABC):
    PATTERN_42: list[list[int]] = [[15, 0, 15, ...], ...]
```

#### 2. `second_loop()` fonction imbriquée dans `Kruksal.generate()`
`second_loop` est une closure définie à l'intérieur de `generate()`.  
C'est une méthode privée déguisée — difficile à tester, à lire, et non réutilisable.  
**Recommandation** : extraire en `_second_loop(self, maze, pattern_cells, pattern_neighbors)`.

#### 3. `_MAX_GLOBAL_ATTEMPTS` constante de module au lieu de constante de classe
```python
# Avant (module-level)
_MAX_GLOBAL_ATTEMPTS = 10

# Après (class-level)
class Kruksal(Algorithm):
    _MAX_GLOBAL_ATTEMPTS: int = 10
```

#### 4. `__init__` vide dans `Kruksal`
`Kruksal.__init__` se contente d'appeler `super().__init__()` — redondant.  
**Recommandation** : supprimer ce `__init__` puisque le parent suffit.

#### 5. Attributs publics de `Maze` (`grid`, `width`, `height`)
Les vues et les algorithmes accèdent directement aux attributs internes de `Maze`.  
**Recommandation** : exposer `width` et `height` en propriétés en lecture seule (`@property`), et envisager un protocole `MazeProtocol` pour le long terme.

#### 6. `solution_path` public dans `MazeGenerator`
`self.solution_path` est public mais jamais alimenté (`get_solution()` lève toujours `ValueError`).  
**Recommandation** : implémenter `PathFinder` et alimenter `solution_path` dans `generate()`.

---

## 2. Bilan SOLID

### S — Single Responsibility

| Classe | SRP respecté ? | Note |
|--------|---------------|------|
| `Maze` | ⚠️ | Contient `PATTERN_42` (responsabilité de génération, pas de données) |
| `MazeValidator` | ✅ | Responsabilité unique : valider |
| `ConfigParser` | ✅ | Parsing et validation de config |
| `Algorithm` | ✅ | Logique partagée + contrat abstrait |
| `Backtracker` | ✅ | Un seul algorithme |
| `Kruksal` | ⚠️ | `second_loop` imbriqué alourdit la classe |
| `MazeGenerator` | ⚠️ | Trop de responsabilités : factory + seed + validation |
| `MazeController.run()` | ⚠️ | Méthode monolithique : config + génération + vue + écriture fichier |
| `TerminalView` | ✅ | `play()` unifié, `_render()` unique — duplication supprimée |

**Actions :**
- Sortir `PATTERN_42` de `Maze`
- Extraire `second_loop` en méthode privée de `Kruksal`
- Décomposer `MazeController.run()` en sous-méthodes (`_generate()`, `_render()`, `_write_output()`)

---

### O — Open/Closed

| Élément | État | Problème |
|---------|------|---------|
| Ajout d'un algorithme | ✅ (quasi) | Créer une sous-classe suffit, mais `_build_algorithm()` doit être édité (if/elif) |
| Ajout d'une vue | ❌ | `MazeController` connaît les noms `TerminalView`, `CursesView` en dur |
| `_validate_coordinates()` | ⚠️ | Mélange validation de dimensions et de positions via `if key in [...]` |

**Actions :**
- Remplacer le `if/elif` de `_build_algorithm()` par un registre de classes (`dict`) ou une factory injectable
- Créer `AbstractView` et injecter la vue dans le contrôleur
- Séparer `_validate_coordinates()` en `_validate_dimensions()` + `_validate_position()`

---

### L — Liskov Substitution ✅ CORRIGÉ

~~Violation active~~ **Corrigée le 05/04/2026** : `Backtracker.generate()` retourne désormais `list[tuple[int, int, str]]`, identique à `Kruksal.generate()`.

```python
# Avant — Backtracker (violait LSP)
track = ['N', 'E', 'BACK', 'S', ...]   # list[str]

# Après — Backtracker et Kruskal (même format)
track = [(0, 0, 'E'), (1, 0, 'S'), ...]  # list[tuple[int, int, str]]
```

`MazeController` n'a plus besoin de `isinstance(track[0], tuple)`.  
`TerminalView.play()` traite les deux algorithmes avec la même boucle.  
Le `BACK` (backtrack) est absorbé silencieusement dans l'algorithme — seules les étapes de mur cassé apparaissent dans le track.

---

### I — Interface Segregation ⚠️

Pas d'interface/protocole commun entre `TerminalView` et `CursesView`.  
`MazeController` sélectionne la vue par un `if view_mode == "curse"`.

**Recommandation** :
```python
# view/abstract_view.py
from abc import ABC, abstractmethod

class AbstractView(ABC):
    @abstractmethod
    def play(self) -> None: ...

    @abstractmethod
    def print_result(self) -> None: ...
```
Les deux vues implémentent `AbstractView`, le contrôleur ne connaît que l'interface.

---

### D — Dependency Inversion ⚠️

| Dépendance | Direction | Problème |
|-----------|-----------|---------|
| `TerminalView` → `Maze.grid` | Concrète | Accès direct aux attributs internes |
| `MazeController` → `TerminalView`, `CursesView` | Concrète | Module de haut niveau dépend de détails |
| `Algorithm` → `Maze` | Concrète | Acceptable pour l'instant, `MazeProtocol` serait l'idéal |
| `Kruksal` → `MazeValidator` | Concrète | Acceptable (même couche) |

**Recommandation principale** : créer un `Protocol` ou `AbstractView` et injecter la dépendance dans `MazeController`.

---

## 3. Notes par module

| Module | Note /5 | Résumé |
|--------|---------|--------|
| `model/maze.py` | **4/5** | Propre et fonctionnel — PATTERN_42 à sortir |
| `model/maze_validator.py` | **4.5/5** | Excellent SRP, BFS correct, bien documenté |
| `model/config_parser.py` | **3.5/5** | Fonctionnel, bug off-by-one persistant, alias `recursive_backtracker` résiduel |
| `model/path_finder.py` | **4/5** | BFS implémenté, `find_k_shortest_paths()` opérationnel, méthodes redondantes supprimées |
| `mazegen/algorithm.py` | **4/5** | Bonne abstraction — PATTERN_42 à déplacer ici |
| `mazegen/backtracker.py` | **4.5/5** | Propre, LSP corrigé, format unifié avec Kruskal |
| `mazegen/kruksal.py` | **3/5** | Logique complexe pertinente — second_loop à refactoriser |
| `mazegen/maze_generator.py` | **3.5/5** | API propre — get_solution() cassée, alias résiduel |
| `controller/maze_controller.py` | **3.5/5** | isinstance supprimé, format fichier à corriger, run() encore monolithique |
| `view/terminal_view.py` | **4.5/5** | _render() unique, play() unifié, solution toggle [S], couleur 42 toggle [C] |
| `view/menu.py` | **4/5** | Nouveau fichier, Enter en mode raw corrigé (\r) |
| `view/mlx_view.py` | **0/5** | Stub total (bonus) |
| `tests/test_maze.py` | **3/5** | Implémenté — coverage partielle |
| `tests/test_maze_generator.py` | **3/5** | Implémenté — coverage partielle |
| `tests/test_path_finder.py` | **0/5** | Stub total |
| `Makefile` | **0/5** | Stub total — 🔴 OBLIGATOIRE |

---

## 4. Note globale

| Catégorie | Note |
|-----------|------|
| Architecture générale / MVC | 15/20 |
| Respect POO (encapsulation, héritage, polymorphisme) | 16/20 |
| Respect SOLID | 14/20 |
| Complétude fonctionnelle (sujet) | 14/20 |
| Qualité des tests | 10/20 |
| **Note globale estimée** | **14/20** |

---

## 5. Actions prioritaires restantes

| Priorité | Action | Fichier(s) |
|----------|--------|-----------|
| 🔴 CRITIQUE | Corriger le format du fichier de sortie (entrée, sortie, chemin) | `controller/maze_controller.py` |
| 🔴 CRITIQUE | Créer le `Makefile` (install, run, debug, clean, lint, test) | `Makefile` |
| 🟠 IMPORTANT | Créer `AbstractView` et l'injecter dans le contrôleur | `view/`, `controller/` |
| 🟠 IMPORTANT | Déplacer `PATTERN_42` hors de `Maze` | `model/maze.py`, `mazegen/algorithm.py` |
| 🟡 À refactoriser | Extraire `second_loop` en méthode privée de `Kruksal` | `mazegen/kruksal.py` |
| 🟡 À refactoriser | Corriger off-by-one dans `_validate_coordinates()` | `model/config_parser.py` |
| 🟡 À refactoriser | Supprimer l'alias `recursive_backtracker` ou le documenter | `model/config_parser.py`, `mazegen/maze_generator.py` |
| 🟡 À refactoriser | Implémenter `tests/test_path_finder.py` | `tests/test_path_finder.py` |
| 🟡 Amélioration | Décomposer `MazeController.run()` en sous-méthodes | `controller/maze_controller.py` |

### ✅ Déjà corrigé

| Action | Commit |
|--------|--------|
| Implémenter `PathFinder` (BFS, k plus courts chemins) | `5fa9c60` |
| Corriger la violation LSP — `Backtracker` retourne `list[tuple]` | `5fa9c60` |
| Fusionner `_print_with_cursor` + `print_unicode` → `_render()` | `5fa9c60` |
| Fusionner `play()` + `play_kruksal()` → `play()` unique | `5fa9c60` |
| Supprimer `find_path()`, `has_unique_path()`, `_dirs_to_connections()` | `5fa9c60` |
| Corriger la touche Entrée en mode raw (`\r` au lieu de `\n`) | `5fa9c60` |
| Solution cachée par défaut, toggle `[S]` affiche/cache | `5fa9c60` |
| Toggle `[C]` pour changer la couleur du logo 42 (18 couleurs) | `5fa9c60` |
