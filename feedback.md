# Feedback — A-Maze-ing v2.1 (évaluation May 18 2026)

---

## MANDATORY — Estimation : ~91/100

### IV.2 Usage & IV.3 Config — 10/10 ✅

- `a_maze_ing.py config.txt` correct, nom de fichier conforme
- Toutes les clés obligatoires (WIDTH, HEIGHT, ENTRY, EXIT, OUTPUT_FILE, PERFECT)
- SEED et ALGORITHM en optionnel
- Toutes les erreurs gérées (FileNotFoundError, PermissionError, ValidationError, ValueError, KeyboardInterrupt…)
- `config.txt` par défaut présent dans le repo

### IV.4 Maze Requirements — 22/25

- ✅ Génération aléatoire + reproductibilité via seed
- ✅ Encodage 4-bit par cellule (N/E/S/W)
- ✅ ENTRY ≠ EXIT, dans les bornes (validé ConfigFile + MazeValidator)
- ✅ Connectivité totale (BFS dans `_validate_maze_connectivity`)
- ✅ Symétrie des murs entre voisins (`_validate_adjacent_cells`)
- ✅ Bordures externes fermées (`_validate_maze_boundaries`)
- ✅ Pas de zone 3×3 ouverte (`_has_forbidden_open_areas` + `_no_open_area_around`)
- ✅ Motif « 42 » placé au centre, validé par `_validate_42_pattern`
- ✅ PERFECT = arbre couvrant (Backtracker = unique chemin)
- ❌ **MANQUE** : aucun `print` quand le labyrinthe est trop petit pour le motif 42
  (`place_42_center` retourne silencieusement `set()`) — le sujet l'exige explicitement **(-3 pts)**

### IV.5 Output File Format — 13/15

- ✅ Un hex par cellule, ligne par ligne, `\n` à la fin
- ✅ Ligne vide puis Entry / Exit / Solution
- ✅ Solution encodée en N/E/S/W
- ⚠️ Encodage solution via `directions[-1]` sur les valeurs du dict + `output[:-1]` final :
  fonctionne mais lisibilité/robustesse discutable
- ℹ️ Champs supplémentaires (Seed, Perfect) = bonus acceptable

### V — Visual Representation — 19/20

- ✅ Rendu terminal Unicode / emoji (walls, entry 🏃, exit 🏆)
- ✅ Animation génération track-par-track avec contrôle vitesse (+/-)
- ✅ Show/Hide solution animée (touche S)
- ✅ Re-générer depuis le menu
- ✅ Changement de couleur (touche C = cycle d'emojis)
- ⚠️ Pas de couleur dédiée optionnelle pour les cellules « 42 » **(-1 pt)**

### VI — Code Reusability — 6/10

- ✅ Classe `MazeGenerator` bien encapsulée, API propre (`__init__`, `generate`, `get_maze`, `reset`)
- ✅ `pyproject.toml` configuré (`[project] name = "mazegen"`, packages = ["model", "mazegen"])
- ✅ Documentation dans README : exemple d'utilisation, paramètres, accès à la structure
- ✅ `pip install dist/mazegen-*.whl` documenté dans le README
- ❌ **MANQUE** : fichier `.whl` ou `.tar.gz` absent du repo — il faut lancer `python -m build`
  et committer le fichier généré dans `dist/` **(-4 pts)**

### VII — README Requirements — 9/10 ✅

- ✅ Première ligne italique avec les logins
- ✅ Section Description claire
- ✅ Section Instructions (make install/run/debug/test/lint/clean)
- ✅ Section Ressources + description de l'usage de l'IA
- ✅ Format complet du fichier de configuration (tableau)
- ✅ Algorithmes décrits (Backtracker + Kruksal) + justification des choix
- ✅ Partie réutilisable documentée avec exemple de code
- ✅ Gestion d'équipe : rôles, planning prévu vs réel, bilan, outils
- ⚠️ Le dossier `benchmark/` mentionné dans l'arborescence n'existe pas dans le repo **(-1 pt)**

### III.1/.2 General Rules & Makefile — 12/15

- ✅ Python 3.10+
- ✅ Type hints partout
- ✅ Docstrings PEP 257 sur classes et méthodes
- ✅ Toutes les règles Makefile (install, run, debug, clean, lint, lint-strict, test)
- ✅ `make lint` passe (flake8 + mypy standard)
- ❌ `make lint-strict` → exit code 2 (mypy --strict échoue) **(-2 pts)**
- ⚠️ Pas de `.gitignore` mentionné (requis par III.3) **(-1 pt)**

---

## BONUS — 10/10 ✅

| Bonus | Statut |
|---|---|
| Plusieurs algorithmes (Backtracker + Kruksal) | ✅ |
| Animation pendant la génération | ✅ |

---

## Récapitulatif

| Catégorie | Score estimé |
|---|---|
| Usage + Config (IV.2/IV.3) | 10/10 |
| Maze Requirements (IV.4) | 22/25 |
| Output File (IV.5) | 13/15 |
| Visual Representation (V) | 19/20 |
| Code Reusability (VI) | 6/10 |
| README (VII) | 9/10 |
| General Rules + Makefile (III) | 12/15 |
| **MANDATORY TOTAL** | **~91/100** |
| **BONUS** | **10/10** |

---

## Priorités restantes (par ordre d'impact)

1. **Builder le package** → `python -m build` puis committer `dist/mazegen-*.whl` **+4 pts**
2. **Message console small maze** → 1 `print()` dans `place_42_center` quand trop petit **+3 pts**
3. **mypy --strict** → corriger les erreurs pour valider `make lint-strict` **+2 pts**
4. **Supprimer `benchmark/`** du README ou créer le dossier **+1 pt**
5. **Ajouter `.gitignore`** si absent du repo **+1 pt**
