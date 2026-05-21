*This project has been created as part of the 42 curriculum by gacattan, cyakisan.*

# A-Maze-Ing — Générateur de labyrinthes en Python

Version du sujet: 2.1

> Génération, validation, encodage et affichage d’un labyrinthe configurable.

**Auteurs:** gacattan, cyakisan

## Description

A-Maze-Ing est un projet Python 3.10+ qui lit un fichier de configuration, génère un labyrinthe, calcule le plus court chemin entre l’entrée et la sortie, écrit le résultat dans un fichier de sortie et l’affiche dans un terminal interactif.

Le projet respecte une organisation de type MVC et sépare clairement le parsing de configuration, la génération, la validation, la recherche de chemin et l’affichage. Le paquet réutilisable `mazegen` est fourni en plus du programme principal afin de pouvoir être importé dans un autre projet.

## Instructions

### Installation

```bash
make install
```

Le projet utilise Poetry via le Makefile pour installer les dépendances dans un environnement local `.venv`.

### Exécution

```bash
make run
```

Ou directement:

```bash
python3 a_maze_ing.py config.txt
```

### Debug

```bash
make debug
```

### Tests

```bash
make test
```

### Lint

```bash
make lint
```

```bash
make lint-strict
```

### Nettoyage

```bash
make clean
```

```bash
make fclean
```

## Fichier de configuration

Le fichier de configuration contient une paire `KEY=VALUE` par ligne. Les lignes commençant par `#` sont ignorées.

Clés prises en charge:

| Clé | Obligatoire | Description |
|---|---:|---|
| `WIDTH` | Oui | Largeur du labyrinthe en cellules |
| `HEIGHT` | Oui | Hauteur du labyrinthe en cellules |
| `ENTRY` | Oui | Coordonnées d’entrée au format `x,y` |
| `EXIT` | Oui | Coordonnées de sortie au format `x,y` |
| `OUTPUT_FILE` | Oui | Nom du fichier de sortie |
| `PERFECT` | Oui | `True` pour un labyrinthe parfait |
| `SEED` | Non | Graine de reproductibilité |
| `ALGORITHM` | Non | `backtracker` ou `kruksal` |

Exemple de fichier:

```text
WIDTH=10
HEIGHT=10
ENTRY=0,0
EXIT=9,9
OUTPUT_FILE=maze.txt
PERFECT=True
SEED=42
ALGORITHM=backtracker
```

Le fichier `config.txt` à la racine du dépôt sert de configuration par défaut.

## Format du fichier de sortie

Le programme écrit le labyrinthe sous forme hexadécimale, une ligne par rangée, puis une ligne vide, puis les informations de résolution:

```text
95117D157B
E9287B87D2
D2EE942B92
D03BED042E
BE8417AD03
87EB8543EA
87D06BD03E
8150503E87
EAD07AE903
D47ED47EEE

Seed: 1779368811571294819
Entry: 0, 0
Exit: 9, 9
Solution: EESWSSESEESEEESESSES
Perfect: True
```

Chaque cellule encode ses murs sur 4 bits:

| Bit | Direction |
|---:|---|
| 0 | Nord |
| 1 | Est |
| 2 | Sud |
| 3 | Ouest |

Une cellule complètement fermée vaut `15`. Une cellule ouverte à l’est et au sud vaut `9`.

## Génération du labyrinthe

L’algorithme principal est le **Recursive Backtracker**. Il a été choisi parce qu’il produit naturellement des labyrinthes parfaits, reste simple à lire et se prête bien à une génération reproductible avec une graine.

Un second algorithme, **kruksal**, est aussi disponible comme bonus. Il permet de varier le style des labyrinthes et de garder une alternative de génération.

Le code de génération repose sur la classe réutilisable `MazeGenerator` située dans `mazegen/generation/maze_generator.py`.

## Représentation visuelle

Le projet fournit une vue terminal interactive. Elle affiche les murs, l’entrée, la sortie, le chemin solution et des interactions clavier pour:

1. régénérer et relancer un labyrinthe,
2. afficher ou masquer le plus court chemin,
3. changer les couleurs,
4. ajuster la vitesse d’animation,
5. quitter proprement.

## Module réutilisable

Le module réutilisable peut être utilisé depuis un autre projet Python après installation du paquet buildé (`mazegen-1.0.0-py3-none-any.whl` à la racine du dépôt).

```python
from mazegen import MazeController

controller = MazeController(
    <nom_du_fichier_config>.txt
)

controller.run()
```

L’API exposée permet au minimum de:

1. créer un controller avec des paramètres personnalisés,
2. générer le labyrinthe,
3. visualiser la génération du labyrinthe,
4. récupérer la structure produite, la seed utilisée et un chemin entre l'entrée et la sortie

## Structure du projet

```text
a_maze_ing.py
config.txt
Makefile
pyproject.toml
README.md
mazegen/
tests/
```

Mazegen est construit de cette manière:

1. `model/` pour la structure, la validation et le chemin,
2. `generation/` pour les algorithmes,
3. `view/` pour l’affichage et l’interface terminal,
4. `controller/` pour l’orchestration globale.

## Tests et validation

La base actuelle passe les vérifications automatisées du dépôt: 152 tests réussis et lint OK avec `flake8` et `mypy`.

## Ressources

- [Maze generation](https://weblog.jamisbuck.org/2011/2/7/maze-generation-algorithm-recap.html)
- [Pydantic documentation](https://docs.pydantic.dev/latest/)
- [Colorama documentation](https://pypi.org/project/colorama/)
- [Click documentation](https://click.palletsprojects.com/)

### Usage de l’IA

L’IA a été utilisée pour:

1. aider à structurer le README,
2. reformuler des explications techniques,
3. proposer des cas de test et des points de validation,
4. relire la cohérence documentaire entre le code et le sujet.

Toutes les parties gardées ont été relues et validées manuellement avant intégration.

## Gestion d’équipe

### Rôles

| Login | Rôle principal |
|---|---|
| gacattan | Architecture générale, génération, validation et partie modèle |
| cyakisan | Configuration, interface terminal, intégration, packaging et outillage |

### Planning

1. Mettre en place la structure du projet et le parsing de configuration.
2. Implémenter la génération, la validation et la recherche de chemin.
3. Ajouter l’affichage terminal et les interactions.
4. Stabiliser le packaging, les tests, le lint et la documentation.
5. Ajuster les détails finaux après les retours et les validations.

### Ce qui a bien fonctionné

1. La séparation des responsabilités a facilité les tests.
2. Le format de sortie a pu être validé de façon cohérente avec la structure du labyrinthe.
3. Les vérifications automatisées passent proprement.

### Points d’amélioration

1. Ajouter davantage de tests d’intégration sur le flux interactif.
2. Documenter encore plus précisément les cas limites de configuration.
3. Simplifier certaines sorties terminal très interactives pour les revues futures.

**Planning initial prévu :**
- Semaine 1 : structure du projet, modèle `Maze`, parsing config
- Semaine 2 : algorithmes de génération (Backtracker), validation
- Semaine 3 : rendu terminal, animation, menu interactif
- Semaine 4 : fichier de sortie, PathFinder, tests, packaging

**Comment il a évolué :**
- L'optimisation de l'algorithme Kruskal et la vue terminal nous a pris beaucoup plus de temps que prévu et ont considérablement allongés la durée de création du projet.

### Bilan

**Ce qui a bien marché :**
- L'architecture MVC dès le départ a évité les couplages forts entre les composants.
- L'usage de Pydantic pour la config a rendu la validation robuste avec peu de code.
- Les tests unitaires écrits tôt ont permis de détecter rapidement les régressions lors du refactoring.
- La séparation `Algorithm (ABC)` / sous-classes a rendu l'ajout de Kruksal trivial.

**Ce qui pourrait être amélioré :**
- Mettre en place une CI (GitHub Actions) pour lancer `lint` et `test` automatiquement à chaque push.
- Documenter le format de sortie plus tôt pour éviter les allers-retours.
- Mieux planifier la visualisation dès le début.

### Outils utilisés

- **VS Code** avec l'extension Python et Pylance
- **GitHub** pour le versioning et la collaboration
- **GitHub Copilot** pour l'assistance au code (voir section Ressources)
- **Poetry** pour la gestion des dépendances
- **pytest + pytest-cov** pour les tests
- **mypy + flake8** pour la qualité du code
