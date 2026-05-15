# Évaluation A-Maze-ing — Analyse complète (mise à jour : 2026-05-15)

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
| **Total avec bonus** | **~40 / 42** | **(~95%)** |

---

## Analyse détaillée par section

---

### 1. Règles générales — 5/5 ✅

| Critère | Statut | Notes |
|---------|--------|-------|
| Python 3.10+ | ✅ | `pyproject.toml` : `python = ">=3.10"` |
| Flake8 | ✅ | Configuré dans `pyproject.toml`, max-line-length=80 |
| Gestion des exceptions | ✅ | try/except sur tout le pipeline, `KeyboardInterrupt` inclus |
| Context managers | ✅ | `with open(...)` utilisé partout |
| Type hints + mypy | ✅ | Hints sur toutes les fonctions, `ClassVar`, `TYPE_CHECKING` |
| Docstrings PEP 257 | ✅ | Présents sur toutes les classes et méthodes |

---

### 2. Makefile — 6/6 ✅

| Règle | Statut | Notes |
|-------|--------|-------|
| `install` | ✅ | Poetry + virtualenv |
| `run` | ✅ | Lance via `.venv` |
| `debug` | ✅ | `python3 -m pdb` |
| `clean` | ✅ | Supprime `__pycache__`, `.mypy_cache`, `.pytest_cache` |
| `lint` | ✅ | `flake8` + `mypy` avec **tous** les flags obligatoires du sujet |
| `lint-strict` | ✅ | Présent (optionnel mais implémenté) |

---

### 3. Partie obligatoire — 10/12 ⚠️

#### Ce qui est correct ✅
- Commande : `python3 a_maze_ing.py config.txt` ✅
- Parsing du fichier config (6 clés obligatoires + SEED + ALGORITHM optionnels) via Pydantic ✅
- Génération aléatoire reproductible (seed) ✅
- Chaque cellule a 0 à 4 murs (encodage 4-bits N/E/S/W) ✅
- ENTRY et EXIT valides (dans les bornes, différents, accessibles) ✅
- Bordures extérieures fermées ✅
- Symétrie des murs entre cellules voisines (`MazeValidator._validate_adjacent_cells`) ✅
- Pas de zones 3×3 ouvertes (`_has_forbidden_open_areas`) ✅
- Connectivité totale BFS (hors cellules "42") ✅
- Motif "42" centré, isolé, avec message d'erreur si trop petit ✅
- Mode PERFECT = True → exactement un chemin (CycleChecker via comptage arêtes/nœuds) ✅
- Écriture dans `OUTPUT_FILE` après génération ✅
- Gestion des erreurs sans crash ✅

#### Problèmes identifiés ❌

**1. Format du fichier de sortie non conforme au sujet (risque Moulinette)**

Le sujet impose exactement :
```
<grille hex>

<entry x,y>
<exit x,y>
<chemin: N,E,S,W...>
```

Le code produit :
```
<grille hex>

Seed: 15
Entry: 0, 0
Exit: 4, 2
Solution: ESSS
Perfect: False
```

- Les préfixes `Entry:`, `Exit:`, `Solution:`, `Seed:`, `Perfect:` **ne sont pas dans le spec**.
- Le format des coordonnées : `str((0, 0)).strip("()")` → `"0, 0"` (avec espace) au lieu de `"0,0"`.
- Le séparateur du chemin : lettres concaténées `"ESSS"` vs `"E,S,S,S"` (le sujet utilise des virgules dans les exemples).

> **Impact : perte de ~1–2 points si la Moulinette teste le format exact.**
> Correction dans `menu.py` (ligne ~255) :
> ```python
> output += "\n"
> output += f"{self._controller._config.ENTRY[0]},{self._controller._config.ENTRY[1]}\n"
> output += f"{self._controller._config.EXIT[0]},{self._controller._config.EXIT[1]}\n"
> # Reconstruire le chemin depuis _shortest_path() directement
> path = self._controller._finder._shortest_path()
> output += ",".join(path) + "\n"
> ```

**2. `CycleChecker.has_cycle()` : logique fragile**

La détection de "parfait" compare `edges >= nodes` (théorème arbre couvrant).
Pour un arbre couvrant : `edges = nodes - 1` → parfait si `edges < nodes`.
La condition `edges >= nodes` est correcte pour détecter un cycle, mais elle ne détecte pas le cas où le labyrinthe serait **non-connexe** (edges < nodes - 1). Ce cas est normalement déjà capturé par `MazeValidator`, donc pas un vrai bug en pratique.

---

### 4. Représentation visuelle — 4/4 ✅

- Rendu terminal Unicode avec emojis ✅
- Animation temps réel de la génération (curseur ●) ✅
- ENTRY (🏃) et EXIT (🏆) visibles ✅
- Affichage/masquage du chemin solution (`S`) ✅
- Changement de thème couleur/emoji (`C`) — le motif "42" suit bien le thème (`_EMOJI_INDEX` partagé) ✅
- Contrôle de vitesse (`+`/`-`) ✅
- Quitter (`Q`) ✅
- Régénération depuis le menu principal (`Generate Maze`) ✅ — la touche `R` en vue est un replay (label `REPLAY: R`) ce qui est cohérent et conforme au sujet

---

### 5. Réutilisabilité — 3/4 ⚠️

#### Ce qui est correct ✅
- Classe `MazeGenerator` dans le module `mazegen/` ✅
- API publique stable : `__init__`, `generate()`, `get_maze()`, `reset()` ✅
- Documentation dans README (instantiation, paramètres, accès structure, solution) ✅
- Fichiers buildables (`pyproject.toml` avec setuptools) ✅
- **Package présent à la racine** : `dist/mazegen-1.0.0-py3-none-any.whl` + `dist/mazegen-1.0.0.tar.gz` ✅
- Nom conforme : `mazegen-1.0.0-*` ✅

#### Problème ❌

**Le package `mazegen` importe `model.maze` et `model.maze_validator`**

```python
# mazegen/maze_generator.py
from model.maze import Maze
from model.maze_validator import MazeValidator
```

Or `pyproject.toml` inclut `packages = ["model", "mazegen"]` pour le build, ce qui est correct pour l'installation. Mais cela signifie que **le paquet livré embarque aussi `model/`**, ce qui n'est pas clean (la doc dit "standalone module"). En pratique, `pip install mazegen-1.0.0-*.whl` installera aussi `model`, donc ça fonctionne — mais un correcteur pointilleux pourrait considérer que `model` devrait être intégré dans `mazegen`.

> **Impact : -1 point si le correcteur vérifie l'isolation stricte du paquet.**

---

### 6. README — 10/11 ⚠️

#### Ce qui est correct ✅
- Première ligne italique : `*This project has been created as part of the 42 curriculum by gacattan, cyakisan.*` ✅
- Section Description (implicite dans l'intro) ✅
- Section Instructions (make install, make run…) ✅
- Section Resources (liens + usage IA) ✅
- Format complet du fichier config ✅
- Algorithme choisi et justification ✅
- Réutilisabilité expliquée avec exemple de code ✅
- Gestion d'équipe (rôles, planning, bilan, outils) ✅
- Documentation `mazegen` (instantiation, paramètres, accès maze, solution via PathFinder) ✅

#### Problème ❌

**Section "Description" absente en tant que heading explicite**

Le sujet impose une section `## Description` avec le nom exact.
Le README démarre directement sur les fonctionnalités sans heading `## Description`.

> Correction simple : ajouter `## Description` avant le paragraphe d'intro.

---

## Résumé des corrections prioritaires

| Priorité | Fichier | Action |
|----------|---------|--------|
| 🔴 Haute | `view/menu.py` | Corriger le format de sortie `OUTPUT_FILE` (supprimer les préfixes `Entry:`, `Exit:`, `Solution:`, `Seed:`, `Perfect:`, corriger les coordonnées `0,0` et le chemin `N,E,S,...`) |
| 🟠 Moyenne | `README.md` | Ajouter le heading `## Description` explicite |

| 🟢 Optionnel | `mazegen/` | Intégrer les classes `Maze` et `MazeValidator` directement dans le paquet pour l'isolation complète |

---

## Bonuses confirmés

| Bonus | Statut |
|-------|--------|
| Algorithmes multiples (Backtracker + Kruskal) | ✅ |
| Animation de génération temps réel | ✅ |
