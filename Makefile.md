# Makefile

## Rôle
Automatisation des tâches courantes du projet via `make`. Fournit toutes les cibles obligatoires du sujet ainsi que des cibles utilitaires supplémentaires.

## Cibles disponibles

| Cible | Description |
|-------|-------------|
| `install` | Configure Poetry pour créer le venv dans le projet (`.venv/`) et installe toutes les dépendances (`poetry install`) |
| `run` | Lance `install` puis active le venv et exécute `python3 a_maze_ing.py config.txt` |
| `clean` | Supprime tous les caches Python : `__pycache__/`, `.mypy_cache/`, `.pytest_cache/` (racine et sous-répertoires) |
| `fclean` | Appelle `clean` puis supprime également le venv (`.venv/`) et `poetry.lock` |
| `lint` | Lance `install`, puis exécute `flake8` + `mypy` en mode standard (`--warn-return-any`, `--warn-unused-ignores`, `--ignore-missing-imports`, `--disallow-untyped-defs`, `--check-untyped-defs`) |
| `lint-strict` | Lance `install`, puis exécute `flake8` + `mypy --strict` (mode le plus strict) |
| `test` | Lance `install` puis exécute la suite de tests via `pytest tests/` |

## Comportement
- Toutes les cibles qui exécutent du Python activent d'abord le venv via `. .venv/bin/activate` (source POSIX)
- `run`, `lint`, `lint-strict` et `test` appellent `make install` implicitement — pas besoin d'installer manuellement avant chaque commande
- `fclean` est destructif : supprime `poetry.lock` et force une résolution complète des dépendances au prochain `install`

## Note globale : 8/10

## Améliorations possibles
| Priorité | Amélioration |
|----------|-------------|
| Haute | Ajouter `.PHONY` pour toutes les cibles — sans ça, `make` peut ignorer une cible si un fichier du même nom existe |
| Haute | `make run` appelle `make install` à chaque fois — ajouter une cible intermédiaire avec un fichier sentinelle (ex. `.venv/.installed`) pour ne réinstaller qu'en cas de changement |
| Moyenne | `clean` / `fclean` utilisent `rm -rf` sans vérification d'existence — faible risque mais bonne pratique d'ajouter `-f` ou tester avec `[ -d ... ]` |
| Moyenne | Ajouter une cible `debug` qui lance le programme via `pdb` (exigée par le sujet mais absente) |
| Faible | Ajouter une cible `help` qui affiche la liste des cibles disponibles avec leur description |
| Faible | Documenter la version Python requise et les dépendances système (ex. `poetry` doit être installé) |
