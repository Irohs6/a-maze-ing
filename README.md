*This project has been created as part of the 42 curriculum by gacattan, cyakisan.*

# A-Maze-Ing — Générateur de labyrinthes en Python

> Générateur de labyrinthes configurable, animé en temps réel dans le terminal,
> avec motif **42** intégré et encodage hexadécimal du fichier de sortie.

**Auteurs :** gacattan, cyakisan

---

## Description

A-Maze-Ing est un générateur de labyrinthes en Python piloté par un fichier de configuration. Il produit un labyrinthe valide (bordures fermées, murs symétriques, connectivité totale, zones 3×3 interdites) contenant le motif **42** au centre, l'encode en hexadécimal dans un fichier de sortie, et l'affiche avec une animation temps réel dans le terminal. Deux algorithmes de génération sont disponibles : **DFS Recursive Backtracker** (parfait) et **Kruksal modifié** (imparfait). Le code est organisé en architecture **MVC** et le module de génération `mazegen` est livré sous forme de paquet Python installable via `pip`.

---

## Fonctionnalités

- Génération par **DFS Recursive Backtracker** (parfait, reproductible via seed)
- Génération par **Kruksal modifié** (imperfect, avec validation de connectivité)
- Animation temps réel : les murs se creusent sous vos yeux (curseur ●)
- Rendu Unicode propre dans le terminal
- Motif **42** visible au centre du labyrinthe (cellules entièrement isolées)
- Encodage hexadécimal du labyrinthe dans un fichier de sortie
- Validation complète : bordures fermées, symétrie des murs, connectivité BFS, zones 3×3 interdites
- Architecture **MVC** : `model/`, `view/`, `controller/`

---

## Prérequis

- Python 3.10+
- [Poetry](https://python-poetry.org/) pour la gestion des dépendances (installé automatiquement par `make install`)
- Dépendances listées dans `pyproject.toml` (générées dans `requirements.txt`)

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
```

---

## Format du fichier de sortie

```
F9AB...    ← grille hexadécimale, une ligne par rangée

0,0        ← coordonnées d'entrée (x,y)
19,14      ← coordonnées de sortie (x,y)
E,S,E,...  ← chemin solution (N/E/S/W)
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

Le projet suit une architecture **MVC** stricte.

```
a-maze-ing/
│
├── a_maze_ing.py                  # Point d'entrée — parse args, instancie MazeController
│
├── controller/
│   └── maze_controller.py         # Orchestrateur MVC
│
├── mazegen/                       # Paquet réutilisable (installable via pip)
│   ├── algorithm.py               # Classe abstraite Algorithm (ABC)
│   ├── backtracker.py             # Algorithme DFS Backtracker
│   ├── kruksal.py                 # Algorithme Kruksal modifié
│   └── maze_generator.py          # Factory + API publique
│
├── model/
│   ├── maze.py                    # Structure de données (grille 4-bits)
│   ├── maze_validator.py          # Validation structurelle (SRP)
│   ├── config_file.py             # Parsing et validation du fichier config (Pydantic)
│   ├── cycle_checker.py           # Détection de cycles (parfait vs imparfait)
│   └── path_finder.py             # Recherche du chemin le plus court (BFS)
│
├── view/
│   ├── terminal_view.py           # Facade de la vue : gestion des touches et boucle principale
│   ├── terminal_renderer.py       # Rendu ANSI/Unicode, animation, affichage solution
│   └── menu.py                    # Menu interactif (navigation clavier, settings)
│
├── tests/
│   ├── test_maze.py
│   ├── test_maze_generator.py
│   ├── test_config_parser.py
│   ├── test_cycle_checker.py
│   ├── test_maze_validator.py
│   └── test_path_finder.py
│
├── config.txt                     # Configuration par défaut
├── Makefile
├── pyproject.toml
└── requirements.txt
```

### Hiérarchie des algorithmes

```
Algorithm (ABC)
├── Backtracker   — DFS récursif avec stack explicite
└── Kruksal       — Kruksal randomisé avec Union-Find
```

`MazeGenerator` agit comme factory : il instancie la bonne sous-classe selon le paramètre `algorithm`
et expose une API stable (`generate()`, `get_maze()`, `reset()`).

### Choix des algorithmes

**Backtracker (DFS)** a été choisi comme algorithme principal car :
- Il garantit un labyrinthe parfait (un seul chemin entre deux points) naturellement.
- Son implémentation avec une stack explicite est simple, lisible et évite les stack overflows sur les grands labyrinthes.
- Il produit des labyrinthes avec de longs couloirs sinueux, visuellement intéressants.

**Kruksal modifié** a été ajouté en complément car :
- Il repose sur un Union-Find, une structure de données classique en algorithmique.
- Il génère des labyrinthes avec un aspect plus uniforme et aléatoire (pas de biais de direction).
- Son inclusion permet de satisfaire l'exigence de bonus « multiple algorithmes ».

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
- `test_path_finder.py` — BFS, reconstruction du chemin
- `test_cycle_checker.py` — détection de cycles (parfait / imparfait)
- `test_maze_validator.py` — validation structurelle complète

---

## Ressources

- [Théorie des labyrinthes — Wikipedia](https://fr.wikipedia.org/wiki/G%C3%A9n%C3%A9ration_de_labyrinthe)
- [Recursive Backtracker — jamisbuck.org](https://weblog.jamisbuck.org/2010/12/27/maze-generation-recursive-backtracker)
- [Kruksal's algorithm — Wikipedia](https://en.wikipedia.org/wiki/Kruksal%27s_algorithm)
- [Union-Find / Disjoint Set — Wikipedia](https://en.wikipedia.org/wiki/Disjoint-set_data_structure)
- [Pydantic v2 Documentation](https://docs.pydantic.dev/latest/)
- [ANSI escape codes — Wikipedia](https://en.wikipedia.org/wiki/ANSI_escape_code)

### Usage de l'IA (GitHub Copilot)

| Tâche | Utilisation |
|-------|-------------|
| Structure initiale MVC | Suggestions d'organisation des modules, revue de la séparation des responsabilités |
| `MazeValidator` | Aide à la rédaction des cas de validation (symétrie des murs, connectivité BFS) |
| Docstrings | Aide à la rédaction des docstrings PEP 257 sur les classes et fonctions |
| Tests unitaires | Suggestions de cas de test paramétrés (pytest.mark.parametrize) |

Tout le code généré a été relu, testé et compris avant intégration. Aucune section critique (algorithmes, validation, rendu) n'a été copiée-collée sans compréhension et adaptation.

---

## Gestion d'équipe

### Rôles

| Login | Contributions principales |
|-------|--------------------------|
| gacattan | Architecture MVC, modèle `Maze`, `MazeValidator`, `CycleChecker`, algorithme `Backtracker`, vues `TerminalView`, `TerminalRenderer`, animation ANSI, `PathFinder`, tests unitaires |
| cyakisan | `ConfigFile` (Pydantic), algorithme `Kruksal`, refactoring `Algorithm`, vue `Menu`, `TerminalView`, `TerminalRenderer`, animation ANSI, `Makefile`, `pyproject.toml`, tests unitaires |

### Planning

**Planning initial prévu :**
- Semaine 1 : structure du projet, modèle `Maze`, parsing config
- Semaine 2 : algorithmes de génération (Backtracker), validation
- Semaine 3 : rendu terminal, animation, menu interactif
- Semaine 4 : fichier de sortie, PathFinder, tests, packaging

**Comment il a évolué :**
- Le packaging `mazegen` a été traité en parallèle plutôt qu'en fin de projet, ce qui a facilité les tests d'intégration.

### Bilan

**Ce qui a bien marché :**
- L'architecture MVC dès le départ a évité les couplages forts entre les composants.
- L'usage de Pydantic pour la config a rendu la validation robuste avec peu de code.
- Les tests unitaires écrits tôt ont permis de détecter rapidement les régressions lors du refactoring.
- La séparation `Algorithm (ABC)` / sous-classes a rendu l'ajout de Kruksal trivial.

**Ce qui pourrait être amélioré :**
- Mettre en place une CI (GitHub Actions) pour lancer `lint` et `test` automatiquement à chaque push.
- Documenter le format de sortie plus tôt pour éviter les allers-retours.

### Outils utilisés

- **VS Code** avec l'extension Python et Pylance
- **GitHub** pour le versioning et la collaboration
- **GitHub Copilot** pour l'assistance au code (voir section Ressources)
- **Poetry** pour la gestion des dépendances
- **pytest + pytest-cov** pour les tests
- **mypy + flake8** pour la qualité du code
