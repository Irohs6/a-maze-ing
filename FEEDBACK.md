# Feedback — A-Maze-ing (v2.1)

**Date d'évaluation :** 06/05/2026  
**Auteurs :** gacattan, cyakisan  
**Note globale estimée : 78 / 100**  
**Note réévaluée (après corrections du 06/05/2026) : 82 / 100**

---

## Note globale

| Catégorie | Points max | Points obtenus | Détail |
|-----------|-----------|---------------|--------|
| Partie obligatoire — Génération | 30 | 29 | Très solide ; typo kruskal dans le menu |
| Partie obligatoire — Fichier de sortie | 15 | 14 | Format correct ; ALGORITHM non-optionnel en config |
| Représentation visuelle | 20 | 19 | Animation complète, tous les contrôles présents |
| Réutilisabilité (mazegen) | 15 | 10 | Code excellent, **package .whl manquant** |
| README | 10 | 5 | Beaucoup de sections incomplètes / manquantes |
| Standards (Makefile, flake8, mypy, tests) | 10 | 10 | Tous les targets présents, tests complets |
| **TOTAL** | **100** | **87** | |

> **Note ajustée (pénalités) : ~78/100**  
> Pénalité majeure : package `.whl` absent du dépôt (-5), README non-conforme (-4).

---

### Réévaluation après corrections du 06/05/2026

| Correction | Statut | Impact |
|-----------|--------|--------|
| Typo `"kruksal"` → `"kruskal"` dans `view/menu.py` | ✅ **CORRIGÉ** | +2 pts |
| `ALGORITHM` optionnel avec `default="backtracker"` | ✅ **CORRIGÉ** | +1.5 pts |
| Package `.whl` dans `dist/` | ❌ Toujours absent | -5 pts |
| Première ligne README italique 42 curriculum | ❌ Toujours absent | -2 pts |
| README : planning, retours d'expérience, IA détaillée | ❌ Toujours incomplet | -2 pts |
| README : fichiers fantômes dans le schéma d'archi | ❌ Toujours présent | -1 pt |
| README roadmap obsolète | ❌ Toujours présent | |

> **Note réévaluée : ~82/100** (+4 pts grâce aux 2 corrections)

---

## Évaluation module par module

---

### `a_maze_ing.py` — Point d'entrée

**Note : 9.5 / 10**

| Critère | Statut |
|---------|--------|
| Commande `python3 a_maze_ing.py config.txt` | ✅ |
| Gestion des erreurs (FileNotFoundError, ValueError, KeyError) | ✅ |
| Aucun crash inattendu | ✅ |
| KeyboardInterrupt géré proprement | ✅ |
| Typage complet | ✅ |

**Commentaire :** Entrée propre, minimaliste, conforme. Rien à redire.  
**Déduction (-0.5) :** Le message d'erreur générique de `KeyError` pourrait être plus explicite.

---

### `model/config_file.py` — Parsing de configuration

**Note : 9 / 10** *(était 8/10 — corrigé le 06/05/2026)*

| Critère | Statut |
|---------|--------|
| Format KEY=VALUE, commentaires `#` ignorés | ✅ |
| Tous les champs obligatoires présents | ✅ |
| Validation bounds ENTRY/EXIT | ✅ |
| ENTRY ≠ EXIT | ✅ |
| SEED optionnel (généré si absent) | ✅ |
| Typage Pydantic strict | ✅ |
| ALGORITHM optionnel avec valeur par défaut | ✅ **CORRIGÉ** |

**Commentaire :** Correction propre. L'ajout de `default="backtracker"` règle le crash sur les configs sans ce champ.  
**Déduction restante :**
- `-0.5` : `Field(..., default="backtracker", ...)` est redondant — `...` signifie champ obligatoire et contredit `default`. Utiliser `Field(default="backtracker", pattern=...)` sans le `...`.
- `-0.5` : `VIEW` et autres clés présentes en config réelle sont ignorées silencieusement par Pydantic.

---

### `model/maze.py` — Structure de données

**Note : 10 / 10**

| Critère | Statut |
|---------|--------|
| Encodage 4-bits (N=1, E=2, S=4, W=8) | ✅ |
| `set_wall()` enforce la symétrie automatiquement | ✅ |
| `encode_hex()` correct (une ligne par rangée, un char par cellule) | ✅ |
| Motif `PATTERN_42` centré | ✅ |
| `forty_two_cells` accessible pour exclusions | ✅ |
| Typage complet + docstrings | ✅ |
| Opérations bitwise efficaces | ✅ |

**Commentaire :** Module exemplaire. La symétrie automatique des murs est un excellent choix de conception qui évite toute incohérence. Le motif 42 est bien encapsulé.

---

### `model/maze_validator.py` — Validation

**Note : 9.5 / 10**

| Critère | Statut |
|---------|--------|
| Valeurs cellules dans [0,15] | ✅ |
| Bordures externes toutes fermées | ✅ |
| Symétrie murs adjacents | ✅ |
| Pas de zone 3×3 ouverte | ✅ |
| Connectivité BFS | ✅ |
| Validation motif 42 (ou message si trop petit) | ✅ |
| Collecte de toutes les erreurs (pas de fail-fast) | ✅ |

**Commentaire :** Implémentation complète du SRP — la validation est totalement découplée de la structure. Le BFS de connectivité est correct et exclut bien les cellules 42.  
**Déduction (-0.5) :** La détection de zone 3×3 interdite n'est pas testée dans les tests unitaires visibles.

---

### `model/cycle_checker.py` — Détection de cycles

**Note : 9 / 10**

| Critère | Statut |
|---------|--------|
| Détecte correctement labyrinthe parfait (pas de cycle) | ✅ |
| Détecte correctement labyrinthe imparfait (cycles) | ✅ |
| Exclut les cellules 42 isolées du compte | ✅ |
| Algorithme arête/nœud (heuristique forêt) | ✅ |

**Commentaire :** Approche simple et efficace. L'heuristique `edges >= nodes` est correcte pour un graphe connexe.  
**Déduction (-1) :** L'heuristique peut donner un faux positif si le graphe est déconnecté avec exactement autant d'arêtes que de nœuds. Pour un labyrinthe parfait qui a passé la validation de connectivité, ce cas n'arrive pas — mais le commentaire de code ne l'explique pas.

---

### `model/path_finder.py` — Recherche de chemin

**Note : 9.5 / 10**

| Critère | Statut |
|---------|--------|
| BFS depuis l'entrée vers la sortie | ✅ |
| Chemin retourné en liste de directions N/E/S/W | ✅ |
| `_build_connections_dict()` pour la vue | ✅ |
| Retourne `None` si pas de chemin | ✅ |
| Typage complet | ✅ |

**Commentaire :** BFS propre avec reconstruction par prédécesseur. L'API est bien conçue : le chemin brut est séparé de la représentation vue.  
**Déduction (-0.5) :** Le format de sortie du sujet utilise les directions séparées par des virgules (`N,E,S,W`) — vérifier que la jointure est bien effectuée lors de l'écriture du fichier.

---

### `mazegen/algorithm.py` — Classe abstraite

**Note : 9.5 / 10**

| Critère | Statut |
|---------|--------|
| ABC correctement défini | ✅ |
| Logique partagée (voisins, comptage murs) | ✅ |
| `second_loop()` pour labyrinthe imparfait | ✅ |
| Validation `_no_open_area_around()` pendant la casse | ✅ |
| Typage complet | ✅ |

**Commentaire :** Bonne abstraction. Le `second_loop()` avec validation d'aire ouverte est un vrai travail de conception.  
**Déduction (-0.5) :** Le pourcentage fixe de 15% de murs supplémentaires pour l'imparfait n'est pas configurable ni documenté.

---

### `mazegen/backtracker.py` — DFS Backtracker

**Note : 10 / 10**

| Critère | Statut |
|---------|--------|
| Génération parfaite garantie | ✅ |
| Déterministe via seed | ✅ |
| Stack explicite (pas récursion → pas de stack overflow) | ✅ |
| Appel `second_loop()` si imparfait | ✅ |

**Commentaire :** Implémentation textbook, robuste. Le choix d'une stack explicite plutôt que la récursion est judicieux pour les grands labyrinthes.

---

### `mazegen/kruskal.py` — Kruskal modifié

**Note : 9.5 / 10**

| Critère | Statut |
|---------|--------|
| Union-Find correct | ✅ |
| Génère un labyrinthe parfait | ✅ |
| Exclut les murs des cellules 42 | ✅ |
| Déterministe via seed | ✅ |
| Appel `second_loop()` si imparfait | ✅ |

**Commentaire :** Kruskal randomisé bien implémenté. L'exclusion des cellules 42 du union-find est correctement gérée.  
**Déduction (-0.5) :** Le nom du fichier (`kruskal.py`) diverge du nom cité dans le README et le menu (`kruksal`) — source de confusion.

---

### `mazegen/maze_generator.py` — Factory publique

**Note : 10 / 10**

| Critère | Statut |
|---------|--------|
| API publique stable (`generate()`, `get_maze()`, `reset()`) | ✅ |
| Factory pattern pour les algorithmes | ✅ |
| Valide le labyrinthe après génération | ✅ |
| Utilisable en dehors du projet | ✅ |
| Documenté avec exemple d'usage | ✅ |

**Commentaire :** Module exemplaire pour la réutilisabilité. L'API est simple, stable et bien documentée.

---

### `controller/maze_controller.py` — Orchestrateur MVC

**Note : 9.5 / 10**

| Critère | Statut |
|---------|--------|
| Séparation nette model / view / controller | ✅ |
| Pipeline complet (config → génération → path → view) | ✅ |
| Injection de dépendances propre | ✅ |

**Commentaire :** Le contrôleur est fin et délègue correctement. L'architecture MVC est bien respectée.  
**Déduction (-0.5) :** Pas de gestion explicite du cas où `PathFinder.find()` retourne `None` (labyrinthe sans chemin malgré la validation).

---

### `view/terminal_renderer.py` — Rendu et animation

**Note : 9.5 / 10**

| Critère | Statut |
|---------|--------|
| Rendu Unicode des murs | ✅ |
| Animation step-by-step | ✅ |
| SPACE (pause), N (step), +/- (vitesse), C (couleurs), S (solution) | ✅ |
| 7 thèmes de couleurs | ✅ |
| Thèmes séparés pour le motif 42 | ✅ |
| Buffer flush unique (efficacité) | ✅ |
| `_erase_corners()` pour le rendu lisse | ✅ |

**Commentaire :** Rendu sophistiqué et soigné. Les contrôles interactifs couvrent toutes les exigences du sujet et plus encore.  
**Déduction (-0.5) :** La barre de statut en bas de l'écran peut être tronquée sur les petits terminaux sans gestion explicite.

---

### `view/menu.py` — Menu interactif

**Note : 9.5 / 10** *(était 7.5/10 — corrigé le 06/05/2026)*

| Critère | Statut |
|---------|--------|
| Navigation clavier (flèches, Entrée) | ✅ |
| Regénération du labyrinthe | ✅ |
| Modification de tous les paramètres config | ✅ |
| Validation Pydantic des nouvelles valeurs | ✅ |
| Rollback en cas d'erreur | ✅ |
| Typo `"kruskal"` corrigé | ✅ **CORRIGÉ** |

**Commentaire :** Menu complet et bien pensé avec rollback. La correction du typo rend le choix Kruskal pleinement fonctionnel.  
**Déduction restante :**
- `-0.5` : Pas de confirmation avant la regénération si un labyrinthe est déjà affiché.

---

### `view/terminal_view.py` + `terminal_launcher.py` + `terminal_spawn_runner.py` + `terminal_backends.py`

**Note : 9 / 10**

| Critère | Statut |
|---------|--------|
| Ouverture d'un nouveau terminal pour l'animation | ✅ |
| Détection XDG du bureau (GNOME, KDE, XFCE...) | ✅ |
| 6 émulateurs supportés (gnome, konsole, xfce4, xterm, alacritty, kitty) | ✅ |
| Fallback sur le terminal courant si aucun trouvé | ✅ |
| Transmission config via JSON temporaire | ✅ |
| Nettoyage du fichier JSON temporaire | ✅ |
| Contrôles interactifs dans la fenêtre spawned | ✅ |

**Commentaire :** Architecture multi-fenêtres bien conçue. La détection XDG est une vraie plus-value de portabilité.  
**Déductions :**
- `-0.5` : Le catch `Exception` trop large dans `terminal_spawn_runner.py` peut masquer des erreurs réelles.
- `-0.5` : La taille de police dynamique par émulateur n'est pas documentée.

---

### `view/ansi_utils.py` — Utilitaires ANSI

**Note : 10 / 10**

| Critère | Statut |
|---------|--------|
| Calculs géométriques centralisés | ✅ |
| Coordonnées ANSI 1-based correctes | ✅ |
| `raw_stdin()` context manager POSIX | ✅ |
| `read_key_or_timeout()` non-bloquant | ✅ |

**Commentaire :** Module utilitaire exemplaire. Toute la logique de positionnement est centralisée ici — excellent SRP.

---

### `tests/` — Tests unitaires

**Note : 9 / 10**

| Module testé | Couverture |
|-------------|-----------|
| `test_maze.py` | ✅ Complet (15+ tests) |
| `test_maze_generator.py` | ✅ Complet (10+ tests) |
| `test_config_parser.py` | ✅ Complet (10+ tests paramétrés) |
| `test_path_finder.py` | ✅ Complet |
| `test_cycle_checker.py` | ✅ Complet |
| `test_maze_validator.py` | ⚠️ Présent mais non vérifié complètement |

**Commentaire :** Couverture solide sur tous les modules critiques. L'usage de `pytest.mark.parametrize` est correct.  
**Déduction (-1) :** Aucun test d'intégration (end-to-end) vérifiant le fichier de sortie complet.

---

### `Makefile`

**Note : 10 / 10**

| Règle | Statut |
|-------|--------|
| `install` | ✅ |
| `run` | ✅ |
| `debug` | ✅ |
| `clean` | ✅ |
| `lint` (flake8 + mypy avec les bons flags) | ✅ |
| `lint-strict` | ✅ |
| `test` | ✅ |

**Commentaire :** Toutes les règles obligatoires sont présentes avec les flags exacts demandés par le sujet.

---

### `README.md`

**Note : 5 / 10**

| Exigence du sujet | Statut |
|------------------|--------|
| Première ligne italique "This project has been created as part of the 42 curriculum by..." | ❌ **ABSENT** |
| Section Description | ✅ (implicite) |
| Section Instructions | ✅ |
| Section Resources + usage détaillé de l'IA (tâches précises, parties du projet) | ⚠️ Trop vague |
| Format complet du fichier de config | ✅ |
| Algorithme choisi + **pourquoi ce choix** | ⚠️ Décrit mais sans justification |
| Quelle partie est réutilisable + comment | ✅ |
| Rôles de chaque membre | ✅ |
| Planning prévu et comment il a évolué | ❌ **ABSENT** |
| Ce qui a bien marché / à améliorer | ❌ **ABSENT** |
| Outils utilisés | ⚠️ Mentionné superficiellement |
| Schéma d'architecture cohérent avec le code réel | ❌ Fichiers fantômes (`curse_view.py`, `mlx_view.py`, `config_parser.py`) |

**Commentaire :** Le contenu technique est là mais les exigences de forme du sujet ne sont pas respectées. La première ligne italique est un critère explicite et vérifiable immédiatement. Le schéma d'architecture liste des fichiers qui n'existent pas.

---

### Package `mazegen` (réutilisabilité pip)

**Note : 6 / 10**

| Exigence | Statut |
|---------|--------|
| `pyproject.toml` présent et correctement configuré | ✅ |
| Code importable indépendamment | ✅ |
| Documentation d'usage dans README | ✅ |
| Exemple d'instanciation et d'utilisation | ✅ |
| **Fichier `.whl` ou `.tar.gz` dans le dépôt** | ❌ **ABSENT** |
| Package nommé `mazegen-*` | ✅ (dans pyproject.toml) |

**Commentaire :** C'est le point **le plus critique** pour l'évaluation. Le sujet est explicite : *"This entire reusable module must be available in a single file suitable for a later installation by pip"* et *"the file must be located at the root of your git repository"*. Le fichier `dist/mazegen-*.whl` doit être construit (`python -m build`) et commité.

**Correction à faire :**
```bash
pip install build
python -m build
git add dist/
git commit -m "build: add mazegen wheel package"
```

---

## Récapitulatif des points critiques à corriger

| Priorité | Problème | Fichier | Statut |
|----------|---------|---------|--------|
| 🔴 CRITIQUE | Package `.whl` absent du dépôt | `dist/` manquant | ❌ À faire |
| 🔴 CRITIQUE | Première ligne README non conforme | [README.md](README.md#L1) | ❌ À faire |
| 🟠 IMPORTANT | README : planning, retours, usage IA détaillé | [README.md](README.md) | ❌ À faire |
| 🟠 IMPORTANT | Schéma archi avec fichiers fantômes | [README.md](README.md#L130) | ❌ À faire |
| 🟡 MINEUR | README roadmap obsolète | [README.md](README.md) | ❌ À faire |
| 🟡 MINEUR | README : justification du choix d'algorithme | [README.md](README.md) | ❌ À faire |
| 🟡 MINEUR | `catch Exception` trop large | [view/terminal_spawn_runner.py](view/terminal_spawn_runner.py) | ❌ À faire |
