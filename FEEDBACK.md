# Feedback — A-Maze-ing

**Date d'évaluation :** 06/05/2026  
**Auteurs :** gacattan, cyakisan  
**Note globale : 92 / 100**

---

## Résumé exécutif

Projet solide, bien architecturé, livré en état de fonctionnement complet. Les 153 tests
passent, `make lint-strict` est propre (flake8 + mypy --strict exit 0), la couverture du
modèle dépasse 94 %. Les deux algorithmes sont implémentés, le motif 42 est en place, les
benchmarks sont présents avec leurs résultats. Le seul manque significatif est l'absence du
wheel `dist/mazegen-*.whl` pré-buildé dans le dépôt.

---

## Détail par critère

### Partie obligatoire (70 pts)

| # | Critère | Points | État | Remarques |
|---|---------|--------|------|-----------|
| 1 | Makefile — `install`, `run`, `debug`, `clean`, `lint`, `test` | 10 / 10 | ✅ | Tous les targets présents et fonctionnels ; `lint-strict` en bonus |
| 2 | Config file — parsing et validation | 9 / 10 | ✅ | Pydantic v2, validators, 7 clés supportées. `-1` : `ALGORITHM` n'est pas listée dans `OPTIONAL_KEYS` (inconsistance mineure) |
| 3 | Structure de labyrinthe + encodage hexadécimal | 10 / 10 | ✅ | Encodage 4-bit correct (N=1, E=2, S=4, W=8), symétrie imposée par `set_wall()` |
| 4 | Algorithme de génération (Backtracker DFS) | 10 / 10 | ✅ | Stack explicite, SEED reproductible, parfait garanti |
| 5 | PathFinder | 10 / 10 | ✅ | BFS, reconstruction du chemin, multi-chemins, dict connexions pour rendu |
| 6 | Visualisation terminal avec animation | 10 / 10 | ✅ | ANSI/Unicode, curseur animé ●, détection auto de 6 émulateurs, fenêtre dédiée |
| 7 | README — ligne d'attribution 42 + documentation | 5 / 5 | ✅ | Première ligne correcte `by gacattan, cyakisan` |
| 8 | Architecture MVC | 5 / 5 | ✅ | `model/`, `view/`, `controller/` strictement séparés, `mazegen/` package indépendant |

**Sous-total obligatoire : 69 / 70**

---

### Bonus (30 pts)

| # | Critère | Points | État | Remarques |
|---|---------|--------|------|-----------|
| B1 | Second algorithme — Kruskal (Union-Find) | 5 / 5 | ✅ | Implémentation correcte, parfait/imparfait, intégré via `ALGO_MAP` |
| B2 | Paquet réutilisable `mazegen` pip-installable | 3 / 5 | ⚠️ | Structure correcte (`pyproject.toml [project]`, `__init__.py`, API propre). `-2` : aucun `dist/mazegen-*.whl` dans le dépôt — un correcteur ne peut pas faire `pip install dist/mazegen-*.whl` sans builder lui-même |
| B3 | Benchmarks (3 scripts + résultats) | 5 / 5 | ✅ | `backtracker`, `kruskal`, `pathfinder` — CSV et Markdown présents |
| B4 | `make lint-strict` (mypy --strict + flake8) | 5 / 5 | ✅ | Exit 0, aucune erreur dans les 34 fichiers sources |
| B5 | Motif 42 au centre | 5 / 5 | ✅ | `PATTERN_42` isolé, protégé contre ENTRY/EXIT, validé |
| B6 | Tests unitaires | 4 / 5 | ✅ | 153 tests, 100 % pass. Modèle : 94–100 % de couverture. `-1` : `view/` à 0 % (inhérent aux tests interactifs, acceptable mais notable) |

**Sous-total bonus : 27 / 30**

---

## Note finale : 69 + 27 = **96 / 100**

> **Ajustement réaliste à 92/100** — un correcteur humain constatera l'absence du `.whl`
> dès le premier `ls dist/` et la présence de `output_validator.py` sans tests ni type hints.
> Ces points sont mineurs mais concrets.

---

## Points forts

- **mypy --strict à 0 erreur** sur 34 fichiers : exploit notable, peu de projets y parviennent.
- **153 tests qui passent tous**, couverture modèle ≥ 94 % : filet de sécurité solide.
- **Validation exhaustive du labyrinthe** (`MazeValidator`) : bordures, symétrie, BFS,
  connectivité, zones 3×3, pattern 42 — bien au-delà du minimum requis.
- **Config Pydantic v2** : validation, normalisation, error messages propres.
- **Architecture claire** : chaque module a une responsabilité unique, les dépendances
  vont dans un sens (model ← mazegen ← controller → view).
- **Benchmarks complets** avec résultats commités — montre une démarche sérieuse.

---

## Points à corriger

### Critique

| Fichier | Problème | Correction |
|---------|----------|------------|
| `dist/` | Absent — le wheel `mazegen-*.whl` n'est pas buildé/commité | `python -m build && git add dist/ && git commit` |

### Mineur

| Fichier | Problème | Correction |
|---------|----------|------------|
| `model/config_file.py` | `ALGORITHM` non listée dans `OPTIONAL_KEYS` | Ajouter `"ALGORITHM"` à la liste |
| `output_validator.py` | `open()` sans `with`, pas de type hints, `sys.exit(1)` style script brut | Refactorer en fonction ou accepter tel quel comme utilitaire externe |
| `view/` | 0 % de couverture de tests | Difficile à tester (terminal interactif) — ajouter des tests unitaires sur les fonctions pures (`ansi_utils.py`, `terminal_backends.py`) |
| `pyproject.toml` | Section `[tool.mypy]` ne reflète pas `--strict` (flags seulement en CLI) | Ajouter `strict = true` dans `[tool.mypy]` pour cohérence |

---

## État des vérifications

```
make lint-strict   → ✅ exit 0  (flake8 OK + mypy --strict : 0 erreur, 34 fichiers)
make test          → ✅ exit 0  (153 passed, 0 failed, 0.56s)
make run           → ✅ fonctionnel (config.txt 60×60, Kruskal, SEED=15)
dist/mazegen-*.whl → ❌ absent
```
