# Audit POO & SOLID — A-Maze-ing — Mise à jour 04/04/2026 (v2)

> Révision complète après implémentation de `PathFinder`, intégration dans
> le contrôleur, affichage du chemin solution en vue terminal, et suppression
> de `curse_view.py`.
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
| PathFinder implémenté | `PathFinder.find_path()`, `find_k_shortest_paths()`, `has_unique_path()` | BFS correct, API propre avec `entry`/`exit` |
| Affichage solution | `TerminalView.show_solution()` | Navigation N/P/Q, détection parfait/imparfait, chemin rendu en ligne |

### ⚠️ À corriger — POO

#### 1. `second_loop()` fonction imbriquée dans `Kruksal.generate()`
`second_loop` est une closure définie à l'intérieur de `generate()`.  
C'est une méthode privée déguisée — difficile à tester, à lire, et non réutilisable.  
**Recommandation** : extraire en `_second_loop(self, maze, pattern_cells)`.

#### 2. Attributs publics de `Maze` (`grid`, `width`, `height`)
Les vues et les algorithmes accèdent directement aux attributs internes de `Maze`.  
**Recommandation** : exposer `width` et `height` en propriétés en lecture seule (`@property`), et envisager un protocole `MazeProtocol` pour le long terme.

#### 3. `get_solution()` toujours cassée dans `MazeGenerator`
`self.solution_path` est public mais jamais alimenté — `get_solution()` lève toujours `ValueError`.  
Le contrôleur contourne via `PathFinder` directement, ce qui double la logique.  
**Recommandation** : alimenter `solution_path` dans `MazeGenerator.generate()` en instanciant `PathFinder` — ou supprimer `get_solution()` si l'usage revient au contrôleur.

#### 4. Bug dans `ConfigParser._parse_optionals()` — double boucle imbriquée
```python
for key in self.OPTIONAL_KEYS:
    for key in self.OPTIONAL_KEYS:   # ← boucle identique en double
```
Les clés optionnelles ne sont jamais appliquées correctement.  
**Recommandation** : supprimer la boucle interne dupliquée.

---

## 2. Bilan SOLID

### S — Single Responsibility

| Classe | SRP respecté ? | Note |
|--------|---------------|------|
| `Maze` | ✅ | Données pures uniquement |
| `MazeValidator` | ✅ | Responsabilité unique : valider |
| `ConfigParser` | ⚠️ | Parsing + validation + double boucle bug |
| `PathFinder` | ✅ | Responsabilité unique : trouver le chemin |
| `Algorithm` | ✅ | Logique partagée + contrat abstrait + utilitaires algo centralisés |
| `Backtracker` | ✅ | Un seul algorithme |
| `Kruksal` | ⚠️ | `second_loop` imbriqué alourdit la classe |
| `MazeGenerator` | ⚠️ | Factory + seed + validation — `get_solution()` cassée |
| `MazeController.run()` | ⚠️ | Méthode monolithique à 6 responsabilités (config, génération, pathfinding, vue, seed, fichier) |
| `TerminalView` | ⚠️ | `play()` et `play_kruksal()` dupliquent la logique d'animation |

**Actions restantes :**
- Extraire `second_loop` en méthode privée de `Kruksal`
- Corriger la double boucle dans `_parse_optionals()`
- Décomposer `MazeController.run()` en `_generate()`, `_solve()`, `_render()`, `_write_output()`

---

### O — Open/Closed

| Élément | État | Problème |
|---------|------|---------|
| Ajout d'un algorithme | ✅ (quasi) | Créer une sous-classe suffit, mais `_build_algorithm()` doit être édité (if/elif) |
| Ajout d'une vue | ❌ | `MazeController` instancie `TerminalView` en dur |
| `_validate_coordinates()` | ⚠️ | Mélange validation de dimensions et de positions via `if key in [...]` |

**Actions :**
- Remplacer le `if/elif` de `_build_algorithm()` par un registre `dict` de classes
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

**Recommandation** : normaliser le format de retour de `generate()` via un `TypedDict` ou un dataclass `Step`.

---

### I — Interface Segregation ⚠️

`curse_view.py` supprimé — la question d'une interface commune est moins urgente mais reste valable pour `MlxView` (bonus).  
`MazeController` instancie `TerminalView` en dur.

**Recommandation** :
```python
# view/abstract_view.py
from abc import ABC, abstractmethod

class AbstractView(ABC):
    @abstractmethod
    def play(self) -> None: ...
    @abstractmethod
    def show_solution(self, paths: list[list[str]], is_perfect: bool) -> None: ...
```

---

### D — Dependency Inversion ⚠️

| Dépendance | Direction | Problème |
|-----------|-----------|---------|
| `TerminalView` → `Maze.grid` | Concrète | Accès direct aux attributs internes |
| `MazeController` → `TerminalView` | Concrète | Module de haut niveau dépend d'un détail |
| `Algorithm` → `Maze` | Concrète | Acceptable pour l'instant |
| `Kruksal` → `MazeValidator` | Concrète | Acceptable (même couche) |
| `MazeValidator` → `Algorithm.PATTERN_42` | Concrète | Acceptable — même package |

**Recommandation principale** : créer `AbstractView` et l'injecter dans `MazeController`.

---

## 3. Notes par module

| Module | Note /5 | Résumé |
|--------|---------|--------|
| `model/maze.py` | **5/5** | Données pures — classe minimaliste et correcte |
| `model/maze_validator.py` | **4.5/5** | Excellent SRP, BFS correct, bien documenté |
| `model/config_parser.py` | **3/5** | Fonctionnel, bug double boucle `_parse_optionals`, alias `recursive_backtracker` résiduel |
| `model/path_finder.py` | **4.5/5** | ✅ BFS implémenté, `find_k_shortest_paths`, `has_unique_path` — API propre |
| `mazegen/algorithm.py` | **4.5/5** | `PATTERN_42` constante de classe, utilitaires centralisés |
| `mazegen/backtracker.py` | **4.5/5** | Propre, lisible |
| `mazegen/kruksal.py` | **3/5** | Logique pertinente — `second_loop` à extraire, LSP violation |
| `mazegen/maze_generator.py` | **3/5** | Factory correcte — `get_solution()` cassée, double alias |
| `controller/maze_controller.py` | **3.5/5** | PathFinder intégré, détection parfait/imparfait ✅ — `run()` monolithique, format fichier incomplet |
| `view/terminal_view.py` | **4/5** | Chemin affiché en ligne ✅, `show_solution` ✅ — duplication `play`/`play_kruksal` persistante |
| `view/mlx_view.py` | **0/5** | Stub total (bonus) |
| `tests/test_maze.py` | **3/5** | Implémenté — coverage partielle |
| `tests/test_maze_generator.py` | **3/5** | Implémenté — coverage partielle |
| `tests/test_path_finder.py` | **0/5** | Stub total — tests à écrire |
| `Makefile` | **0/5** | Stub total — 🔴 OBLIGATOIRE |
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
| Respect POO (encapsulation, héritage, polymorphisme) | 16/20 |
| Respect SOLID | 13/20 |
| Complétude fonctionnelle (sujet) | 14/20 |
| Qualité des tests | 10/20 |
| **Note globale estimée** | **13.5/20** |

---

## 5. Actions prioritaires restantes

| Priorité | Action | Fichier(s) |
|----------|--------|-----------|
| ✅ FAIT | Implémenter `PathFinder` (BFS + k chemins + unicité) | `model/path_finder.py` |
| ✅ FAIT | Intégrer `PathFinder` dans le contrôleur | `controller/maze_controller.py` |
| ✅ FAIT | Afficher le chemin solution en vue terminal (ligne) | `view/terminal_view.py` |
| ✅ FAIT | Détecter labyrinthe parfait/imparfait + navigation N/P/Q | `view/terminal_view.py`, `controller/` |
| ✅ FAIT | Déplacer `PATTERN_42` et méthodes utilitaires dans `Algorithm` | `model/maze.py`, `mazegen/algorithm.py` |
| 🔴 CRITIQUE | Créer le `Makefile` (install, run, debug, clean, lint, test) | `Makefile` |
| 🔴 CRITIQUE | Compléter le format du fichier de sortie (ligne vide + entry + exit + chemin) | `controller/maze_controller.py` |
| 🟠 IMPORTANT | Corriger la violation LSP : normaliser le retour de `generate()` | `mazegen/algorithm.py`, `backtracker.py`, `kruksal.py` |
| 🟠 IMPORTANT | Corriger le bug double boucle dans `_parse_optionals()` | `model/config_parser.py` |
| 🟠 IMPORTANT | Créer `AbstractView` et l'injecter dans le contrôleur | `view/`, `controller/` |
| 🟡 À refactoriser | Extraire `second_loop` en méthode privée de `Kruksal` | `mazegen/kruksal.py` |
| 🟡 À refactoriser | Décomposer `MazeController.run()` en sous-méthodes | `controller/maze_controller.py` |
| 🟡 À refactoriser | Corriger/supprimer `get_solution()` dans `MazeGenerator` | `mazegen/maze_generator.py` |
| 🟡 À refactoriser | Implémenter `tests/test_path_finder.py` | `tests/test_path_finder.py` |
| 🟡 Amélioration | Supprimer l'alias `recursive_backtracker` ou le documenter | `model/config_parser.py`, `mazegen/maze_generator.py` |
