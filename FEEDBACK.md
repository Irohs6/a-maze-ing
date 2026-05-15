# Évaluation A-Maze-ing — Feedback complet (2026-05-15)

---

## Note globale estimée

| Catégorie | Score | Max |
|-----------|------:|----:|
| Règles générales | 5 | 5 |
| Makefile | 6 | 6 |
| Partie obligatoire | 10 | 12 |
| Représentation visuelle | 4 | 4 |
| Réutilisabilité | 3 | 4 |
| README | 10 | 11 |
| **Total** | **38** | **42** |
| Bonus (2 algos + animation) | **+2** | — |
| **Total avec bonus** | **~40 / 42 (~95%)** | |

---

## 1. Règles générales — 5/5 ✅

| Critère | Statut | Notes |
|---------|:------:|-------|
| Python 3.10+ | ✅ | `python = ">=3.10"` dans `pyproject.toml` |
| flake8 | ✅ | Configuré via `[tool.flake8]`, `max-line-length = 80` |
| Gestion des exceptions | ✅ | try/except sur tout le pipeline, `KeyboardInterrupt` inclus |
| Context managers | ✅ | `with open(...)` utilisé partout |
| Type hints + mypy | ✅ | Hints sur toutes les fonctions, `ClassVar`, `TYPE_CHECKING`, annotations futures |
| Docstrings PEP 257 | ✅ | Présents sur toutes les classes et méthodes publiques |

**Seul bémol flake8 (non bloquant) :** `terminal_renderer.py` contient deux imports inutilisés (`entry_points`, `re.I`) et deux lignes > 80 chars. Ces erreurs préexistaient et ne sont pas liées aux dernières modifications.

---

## 2. Makefile — 6/6 ✅

| Règle | Statut | Notes |
|-------|:------:|-------|
| `install` | ✅ | `poetry install` avec virtualenv local |
| `run` | ✅ | Dépend de `install`, lance via `.venv` |
| `debug` | ✅ | `python3 -m pdb` |
| `clean` | ✅ | Supprime `__pycache__`, `.mypy_cache`, `.pytest_cache` |
| `lint` | ✅ | `flake8` + `mypy` avec **exactement** les flags obligatoires du sujet |
| `lint-strict` | ✅ | Présent (`mypy --strict`) |
| `.PHONY` | ✅ | Déclaré pour toutes les cibles |
| Silencieux | ✅ | `.SILENT:` en tête, appels récursifs avec `-s` → aucun écho de commandes |

---

## 3. Partie obligatoire — 10/12 ⚠️

### Ce qui est correct ✅

- `python3 a_maze_ing.py config.txt` ✅
- Parsing via Pydantic : 6 clés obligatoires + `SEED`, `ALGORITHM` optionnels ✅
- Génération aléatoire reproductible (seed) ✅
- Encodage 4-bits par cellule (N=1, E=2, S=4, W=8) ✅
- ENTRY et EXIT : dans les bornes, différents, validés ✅
- Bordures extérieures toutes fermées ✅
- Symétrie des murs vérifiée (`_validate_adjacent_cells`) ✅
- Pas de zones 3×3 ouvertes (`_has_forbidden_open_areas`) ✅
- Connectivité totale BFS (hors cellules "42") ✅
- Motif "42" centré, cellules isolées, message d'erreur si labyrinthe trop petit ✅
- `PERFECT=True` → un seul chemin (`CycleChecker`) ✅
- Écriture dans `OUTPUT_FILE` après génération ✅
- Gestion des erreurs sans crash (FileNotFoundError, PermissionError, ValidationError…) ✅

### Problèmes identifiés ❌

**1. Format du fichier de sortie non conforme au sujet**

Le sujet impose strictement :
```
<grille hex, une ligne par rangée>
<ligne vide>
<entry x,y>
<exit x,y>
<chemin: N,E,S,W,...>
```

Le code produit actuellement (`menu.py`) :
```
<grille hex>

Seed: 15
Entry: 0, 0
Exit: 4, 2
Solution: ESSS
Perfect: False
```

Problèmes :
- Champs supplémentaires hors spec : `Seed:`, `Perfect:` — la Moulinette ne les attend pas.
- Préfixes `Entry:` / `Exit:` / `Solution:` — hors spec.
- Format des coordonnées : `str((0, 0)).strip("()")` → `"0, 0"` (espace) au lieu de `"0,0"`.
- Chemin concaténé `"ESSS"` au lieu de `"E,S,S,S"` (le sujet montre des lettres séparées par virgules).

> **Impact : −1 à −2 pts si la Moulinette valide le format exact.**

Correction recommandée dans `view/menu.py` :
```python
entry_cfg = self._controller._config.ENTRY
exit_cfg  = self._controller._config.EXIT
path      = self._controller._finder._shortest_path()
output += "\n"
output += f"{entry_cfg[0]},{entry_cfg[1]}\n"
output += f"{exit_cfg[0]},{exit_cfg[1]}\n"
output += ",".join(path) + "\n"
```

**2. `CycleChecker.has_cycle()` : cas non-connexe non détecté**

La formule `edges >= nodes` détecte correctement un cycle (arbre couvrant = `nodes - 1` arêtes).
Mais si le graphe était **non-connexe** (`edges < nodes - 1`), `has_cycle()` retournerait `False` à tort, indiquant "parfait" alors que le labyrinthe est brisé.
Ce cas est normalement déjà bloqué par `MazeValidator._validate_maze_connectivity()`, donc pas de bug observable en pratique — mais la logique est fragile si jamais `MazeValidator` est contourné.

---

## 4. Représentation visuelle — 4/4 ✅

| Interaction | Statut | Notes |
|-------------|:------:|-------|
| Régénération | ✅ | Via le menu principal "Generate Maze" |
| Afficher/masquer la solution | ✅ | Touche `S` |
| Changer les couleurs | ✅ | Touche `C` — cycle sur `_EMOJI_LIST`, motif "42" suit le thème (`_EMOJI_INDEX` partagé) |
| Replay de l'animation | ✅ | Touche `R` (label `REPLAY: R` affiché) |
| Contrôle vitesse | ✅ | Touches `+` / `-` |
| Quitter | ✅ | Touche `Q` |
| ENTRY / EXIT visibles | ✅ | 🏃 et 🏆 |
| Motif "42" distinct | ✅ | `_EMOJI_LIST[1]` inversé |

---

## 5. Réutilisabilité — 3/4 ⚠️

### Ce qui est correct ✅

- Classe `MazeGenerator` dans `mazegen/` ✅
- API publique stable : `__init__`, `generate()`, `get_maze()`, `reset()` ✅
- Documentation dans le README (instantiation, paramètres, accès grille, solution) ✅
- `pyproject.toml` avec setuptools configuré pour le build ✅
- Package présent à la racine : `dist/mazegen-1.0.0-py3-none-any.whl` + `dist/mazegen-1.0.0.tar.gz` ✅
- Nom conforme au sujet : `mazegen-1.0.0-*` ✅

### Problème ❌

**Le paquet `mazegen` embarque `model/` comme dépendance externe**

```python
# mazegen/maze_generator.py
from model.maze import Maze
from model.maze_validator import MazeValidator
```

Le `pyproject.toml` inclut `packages = ["model", "mazegen"]`, donc le `.whl` embarque bien les deux — `pip install` fonctionnera. Mais le sujet demande un "standalone module" : idéalement `Maze` et `MazeValidator` seraient intégrés directement dans `mazegen/` sans dépendre d'un paquet `model` externe.

> **Impact : −1 pt si le correcteur vérifie l'isolation stricte.**

---

## 6. README — 10/11 ⚠️

### Ce qui est correct ✅

- Première ligne italique obligatoire présente ✅
- Sections Instructions, Resources ✅
- Format complet du fichier config ✅
- Algorithmes choisis et justifiés ✅
- Réutilisabilité expliquée avec exemple de code ✅
- Usage IA documenté (tableau par tâche) ✅
- Gestion d'équipe : rôles, planning, bilan, outils ✅
- Documentation `mazegen` : instantiation, paramètres, accès maze ✅

### Problème ❌

**Pas de section `## Description` avec ce nom exact**

Le sujet demande une section "Description". Le README commence directement par un bloc de fonctionnalités sans heading `## Description`.

> Correction : ajouter `## Description` comme heading avant le paragraphe d'introduction.

---

## Résumé des corrections prioritaires

| Priorité | Fichier | Action |
|----------|---------|--------|
| 🔴 Haute | `view/menu.py` | Corriger le format de `OUTPUT_FILE` : supprimer `Seed:` / `Perfect:` / préfixes, corriger `0,0` et chemin `N,E,S,...` |
| 🟠 Moyenne | `README.md` | Ajouter le heading `## Description` |
| 🟢 Optionnel | `mazegen/` | Intégrer `Maze` et `MazeValidator` dans le paquet pour isolation complète |

---

## Bonuses confirmés

| Bonus | Statut |
|-------|:------:|
| Algorithmes multiples (Backtracker + Kruksal) | ✅ |
| Animation de génération temps réel | ✅ |
