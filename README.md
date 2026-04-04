# A-Maze-Ing — Générateur de labyrinthes en Python

*Voici la voie*

> Générateur de labyrinthes configurable, animé en temps réel dans le terminal,
> avec motif **42** intégré et encodage hexadécimal du fichier de sortie.

**Auteurs :** gacattan, cyakisan

---

## Fonctionnalités

- Génération par **DFS Recursive Backtracker** (parfait, reproductible via seed)
- Génération par **Kruskal modifié** (imperfect, avec validation de connectivité)
- Animation temps réel : les murs se creusent sous vos yeux (curseur ●)
- Rendu Unicode propre dans le terminal ou via `ncurses`
- Motif **42** visible au centre du labyrinthe (cellules entièrement isolées)
- Encodage hexadécimal du labyrinthe dans un fichier de sortie
- Validation complète : bordures fermées, symétrie des murs, connectivité BFS, zones 3×3 interdites
- Architecture **MVC** : `model/`, `view/`, `controller/`

---

## Prérequis

- Python 3.10+
- Dépendances listées dans `requirements.txt`

---

## Installation et lancement

```bash
# Installer les dépendances
make install

# Lancer avec le fichier de configuration par défaut
make run

# Lancer en mode debug (pdb)
make debug

# Lancer les tests
make test

# Lint (flake8 + mypy)
make lint

# Nettoyer les caches
make clean
```

Ou directement :

```bash
python3 a_maze_ing.py config.txt
```

---

## Fichier de configuration

Le fichier `config.txt` contient des paires `CLE=VALEUR`. Les lignes commençant par `#` sont ignorées.

| Clé | Obligatoire | Description | Exemple |
|-----|-------------|-------------|---------|
| `WIDTH` | ✅ | Largeur en cellules | `WIDTH=20` |
| `HEIGHT` | ✅ | Hauteur en cellules | `HEIGHT=15` |
| `ENTRY` | ✅ | Coordonnée d'entrée (x,y) | `ENTRY=0,0` |
| `EXIT` | ✅ | Coordonnée de sortie (x,y) | `EXIT=19,14` |
| `OUTPUT_FILE` | ✅ | Fichier de sortie hexadécimal | `OUTPUT_FILE=maze.txt` |
| `PERFECT` | ✅ | Chemin unique entrée→sortie | `PERFECT=True` |
| `SEED` | — | Graine pour la reproductibilité | `SEED=42` |
| `ALGORITHM` | — | Algorithme (`backtracker` ou `kruksal`) | `ALGORITHM=backtracker` |
| `VIEW` | — | Mode d'affichage (`terminal` ou `curse`) | `VIEW=terminal` |

Exemple de fichier `config.txt` :

```
WIDTH=20
HEIGHT=15
ENTRY=0,0
EXIT=19,14
OUTPUT_FILE=maze.txt
PERFECT=True
SEED=42
ALGORITHM=backtracker
VIEW=terminal
```

---

## Format du fichier de sortie

```
F9AB...    ← grille hexadécimale, une ligne par rangée

0,0        ← coordonnées d'entrée (x,y)
19,14      ← coordonnées de sortie (x,y)
E,S,E,...  ← chemin solution (N/E/S/O)
```

Encodage des murs par cellule :

| Mur   | Bit | Valeur |
|-------|-----|--------|
| Nord  | 0   | 1      |
| Est   | 1   | 2      |
| Sud   | 2   | 4      |
| Ouest | 3   | 8      |

Cellule entièrement fermée = `F` (15). Cellule ouverte vers l'est et le sud = `6` (2+4).

---

## Architecture

```
a-maze-ing/
│
├── a_maze_ing.py              # Point d'entrée — parse args, instancie MazeController
│
├── controller/
│   └── maze_controller.py     # Orchestrateur MVC
│
├── mazegen/
│   ├── algorithm.py           # Classe abstraite Algorithm (ABC)
│   ├── backtracker.py         # Algorithme DFS Backtracker
│   ├── kruksal.py             # Algorithme Kruskal modifié
│   └── maze_generator.py      # Factory + API publique du paquet mazegen
│
├── model/
│   ├── maze.py                # Structure de données (grille 4-bits)
│   ├── maze_validator.py      # Validation (SRP séparé de Maze)
│   ├── config_parser.py       # Parsing du fichier config
│   └── path_finder.py         # Recherche du chemin (BFS) — en cours
│
├── view/
│   ├── terminal_view.py       # Animation + rendu Unicode terminal
│   ├── curse_view.py          # Rendu ncurses
│   └── mlx_view.py            # Rendu MLX graphique (bonus — en cours)
│
├── tests/
│   ├── test_maze.py
│   ├── test_maze_generator.py
│   ├── test_config_parser.py
│   └── test_path_finder.py
│
├── config.txt                 # Configuration par défaut
├── Makefile
├── pyproject.toml
└── requirements.txt
```

### Hiérarchie des algorithmes

```
Algorithm (ABC)
├── Backtracker   — DFS récursif, trace list[str]
└── Kruksal       — Kruskal aléatoire, trace list[tuple], retry + validation
```

`MazeGenerator` agit comme factory : il instancie la bonne sous-classe selon le paramètre `algorithm`
et expose une API stable (`generate()`, `get_maze()`, `get_solution()`, `reset()`).

---

## Réutilisabilité du paquet `mazegen`

Le paquet `mazegen` peut être importé indépendamment dans tout projet Python :

```python
from mazegen.maze_generator import MazeGenerator

gen = MazeGenerator(width=20, height=15, seed=42, algorithm='backtracker')
gen.generate()
maze = gen.get_maze()
print(maze.encode_hex())
```

Installation via `pip` (après build) :

```bash
pip install dist/mazegen-*.whl
```

---

## Tests

```bash
pytest tests/ -v
```

Les tests couvrent :
- `test_maze.py` — structure Maze, murs, encodage hex
- `test_maze_generator.py` — génération, déterminisme, API publique
- `test_config_parser.py` — parsing, validation, erreurs
- `test_path_finder.py` — BFS, connectivité (en cours)

---

## Ressources

- [Théorie des labyrinthes — Wikipedia](https://fr.wikipedia.org/wiki/G%C3%A9n%C3%A9ration_de_labyrinthe)
- [Recursive Backtracker — jamisbuck.org](https://weblog.jamisbuck.org/2010/12/27/maze-generation-recursive-backtracker)
- [Kruskal's algorithm — Wikipedia](https://en.wikipedia.org/wiki/Kruskal%27s_algorithm)
- Outils IA utilisés : GitHub Copilot (génération assistée, revue de code, refactoring)

---

## Gestion d'équipe

| Login | Contributions principales |
|-------|--------------------------|
| gacattan | Architecture MVC, modèle Maze, ConfigParser, MazeValidator, refactoring Algorithm, tests |
| cyakisan | Algorithmes de génération (Backtracker, Kruksal), vues (TerminalView, CursesView), animation |

---

## Roadmap

- [ ] Finaliser `PathFinder` (BFS — chemin solution dans le fichier de sortie)
- [ ] Corriger le format du fichier de sortie (coordonnées + chemin)
- [ ] Compléter le `Makefile`
- [ ] Créer `AbstractView` pour découpler les vues du contrôleur
- [ ] Implémenter `MlxView` (affichage graphique — bonus)
- [ ] Builder le paquet `.whl` (`python -m build`)
- [ ] Compléter `tests/test_path_finder.py`
