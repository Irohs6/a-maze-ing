# Audit POO & SOLID — A-Maze-ing — Mise à jour 04/04/2026

> Révision complète intégrant le refactoring de la hiérarchie d'algorithmes
> et le déplacement de `PATTERN_42` + méthodes utilitaires vers `Algorithm`.
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
| Constante bien placée | `Algorithm.PATTERN_42` | Constante de classe dans la bonne couche (génération, pas données) |
| Méthodes utilitaires centralisées | `_get_neighbors_of_cell()`, `_get_direction_neighbor()`, `_get_maze_boundaries()` dans `Algorithm` | `Maze` recentré sur les données pures, logique algo dans la bonne classe |

### ⚠️ À corriger — POO

#### 1. `second_loop()` fonction imbriquée dans `Kruksal.generate()`
`second_loop` est une closure définie à l'intérieur de `generate()`.  
C'est une méthode privée déguisée — difficile à tester, à lire, et non réutilisable.  
**Recommandation** : extraire en `_second_loop(self, maze, pattern_cells, pattern_neighbors)`.

#### ~~2. `_MAX_GLOBAL_ATTEMPTS` constante de module au lieu de constante de classe~~ ✅ FAIT
`_MAX_GLOBAL_ATTEMPTS: int = 10` déplacé en tête du corps de `Kruksal`, avec annotation de type.

#### ~~3. `__init__` vide dans `Kruksal`~~ ✅ FAIT
`__init__` supprimé. L'import `from model.maze import Maze` déplacé sous `TYPE_CHECKING` (+ `from __future__ import annotations`) pour préserver les annotations de type sans import runtime.

#### 4. Attributs publics de `Maze` (`grid`, `width`, `height`)
Les vues et les algorithmes accèdent directement aux attributs internes de `Maze`.  
**Recommandation** : exposer `width` et `height` en propriétés en lecture seule (`@property`), et envisager un protocole `MazeProtocol` pour le long terme.

#### 5. `solution_path` public dans `MazeGenerator`
`self.solution_path` est public mais jamais alimenté (`get_solution()` lève toujours `ValueError`).  
**Recommandation** : implémenter `PathFinder` et alimenter `solution_path` dans `generate()`.

---

## 2. Bilan SOLID

### S — Single Responsibility

| Classe | SRP respecté ? | Note |
|--------|---------------|------|
| `Maze` | ✅ | Données pures uniquement — `PATTERN_42` et méthodes algo déplacés dans `Algorithm` |
| `MazeValidator` | ✅ | Responsabilité unique : valider |
| `ConfigParser` | ✅ | Parsing et validation de config |
| `Algorithm` | ✅ | Logique partagée + contrat abstrait + utilitaires algo centralisés |
| `Backtracker` | ✅ | Un seul algorithme |
| `Kruksal` | ⚠️ | `second_loop` imbriqué alourdit la classe |
| `MazeGenerator` | ⚠️ | Trop de responsabilités : factory + seed + validation |
| `MazeController.run()` | ⚠️ | Méthode monolithique : config + génération + vue + écriture fichier |
| `TerminalView` | ⚠️ | `play()` et `play_kruksal()` dupliquent la logique d'animation |

**Actions restantes :**
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

### L — Liskov Substitution ❌

**Violation active** : `Backtracker.generate()` et `Kruksal.generate()` retournent des types incompatibles.

```python
# Backtracker → list[str]
track = ['N', 'E', 'BACK', 'S', ...]

# Kruksal → list[tuple[int, int, str]]
track = [(0, 0, 'E'), (1, 0, 'S'), ...]
```

`MazeController` compense par un `isinstance(track[0], tuple)` — c'est précisément ce que LSP interdit.  
On ne devrait pas avoir à savoir quelle sous-classe on utilise pour consommer le résultat.

**Recommandation** : normaliser le format de retour de `generate()` — soit toujours `list[str]`, soit toujours `list[tuple]`, soit utiliser un `TypedDict` ou un dataclass `Step`.

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
| `MazeValidator` → `Algorithm` | Concrète | Nécessaire pour accéder à `Algorithm.PATTERN_42` — acceptable |

**Recommandation principale** : créer un `Protocol` ou `AbstractView` et injecter la dépendance dans `MazeController`.

---

## 3. Notes par module

| Module | Note /5 | Résumé |
|--------|---------|--------|
| `model/maze.py` | **5/5** | Données pures — `PATTERN_42` et méthodes algo sortis, clase minimaliste et correcte |
| `model/maze_validator.py` | **4.5/5** | Excellent SRP, BFS correct, bien documenté — importe `Algorithm.PATTERN_42` correctement |
| `model/config_parser.py` | **3.5/5** | Fonctionnel, bug off-by-one persistant, alias `recursive_backtracker` résiduel |
| `model/path_finder.py` | **0/5** | Stub total — 🔴 CRITIQUE |
| `mazegen/algorithm.py` | **4.5/5** | `PATTERN_42` constante de classe, méthodes utilitaires centralisées — référence de la couche algo |
| `mazegen/backtracker.py` | **4.5/5** | Propre, utilise les méthodes du maze, lisible |
| `mazegen/kruksal.py` | **3/5** | Logique complexe pertinente — second_loop à refactoriser, LSP violation |
| `mazegen/maze_generator.py` | **3.5/5** | API propre — get_solution() cassée, alias résiduel |
| `controller/maze_controller.py` | **3/5** | Fonctionne — format fichier erroné, méthode run() trop longue |
| `view/terminal_view.py` | **3.5/5** | Fonctionnelle — duplication play/play_kruksal, pas d'AbstractView |
| `view/curse_view.py` | **3.5/5** | Propre — pas d'AbstractView |
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
| Respect POO (encapsulation, héritage, polymorphisme) | 15/20 |
| Respect SOLID | 12/20 |
| Complétude fonctionnelle (sujet) | 11/20 |
| Qualité des tests | 10/20 |
| **Note globale estimée** | **12.5/20** |

---

## 5. Actions prioritaires restantes

| Priorité | Action | Fichier(s) |
|----------|--------|-----------|
| ✅ FAIT | Déplacer `PATTERN_42` hors de `Maze` → constante de classe dans `Algorithm` | `model/maze.py`, `mazegen/algorithm.py` |
| ✅ FAIT | Déplacer méthodes utilitaires algo hors de `Maze` (`_get_neighbors_of_cell`, etc.) | `model/maze.py`, `mazegen/algorithm.py` |
| 🔴 CRITIQUE | Implémenter `PathFinder` (BFS) | `model/path_finder.py` |
| 🔴 CRITIQUE | Corriger le format du fichier de sortie (entrée, sortie, chemin) | `controller/maze_controller.py` |
| 🔴 CRITIQUE | Créer le `Makefile` (install, run, debug, clean, lint, test) | `Makefile` |
| 🟠 IMPORTANT | Corriger la violation LSP : normaliser le retour de `generate()` | `mazegen/algorithm.py`, `backtracker.py`, `kruksal.py` |
| 🟠 IMPORTANT | Créer `AbstractView` et l'injecter dans le contrôleur | `view/`, `controller/` |
| 🟡 À refactoriser | Extraire `second_loop` en méthode privée de `Kruksal` | `mazegen/kruksal.py` |
| 🟡 À refactoriser | Corriger off-by-one dans `_validate_coordinates()` | `model/config_parser.py` |
| 🟡 À refactoriser | Supprimer l'alias `recursive_backtracker` ou le documenter | `model/config_parser.py`, `mazegen/maze_generator.py` |
| 🟡 À refactoriser | Implémenter `tests/test_path_finder.py` | `tests/test_path_finder.py` |
| 🟡 Amélioration | Décomposer `MazeController.run()` en sous-méthodes | `controller/maze_controller.py` |
