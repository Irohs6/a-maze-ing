# Makefile — Automatisation des tâches courantes du projet.
# Contient les règles obligatoires suivantes :
#   install  : installe les dépendances Python listées dans requirements.txt
#   run      : lance le programme principal avec le fichier config.txt par défaut
#   debug    : lance le programme en mode débogage via pdb
#   clean    : supprime les caches Python (__pycache__, .mypy_cache, .pytest_cache)
#   lint     : exécute flake8 et mypy avec les flags obligatoires du sujet
#   lint-strict : exécute flake8 et mypy en mode strict (optionnel mais recommandé)
# Peut également contenir une règle 'test' pour lancer la suite pytest.

install:
	poetry config virtualenvs.in-project true
	poetry install

run:
	make install
	. .venv/bin/activate; python3 a_maze_ing.py config.txt
	clear

debug:
	make install
	. .venv/bin/activate; python3 -m pdb a_maze_ing.py config.txt

clean:
	rm -rf */__pycache__
	rm -rf __pycache__
	rm -rf */.mypy_cache
	rm -rf .mypy_cache
	rm -rf */.pytest_cache
	rm -rf .pytest_cache

fclean:
	make clean
	rm -rf .venv
	rm -rf poetry.lock
	rm -rf dist

lint:
	make install
	. .venv/bin/activate; python3 -m flake8 && printf '\033[1;32mFlake8 all good !\033[0m\n'; python3 -m mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	make install
	. .venv/bin/activate; python3 -m flake8 && printf '\033[1;32mFlake8 all good !\033[0m\n'; python3 -m mypy . --strict

test:
	make install
	. .venv/bin/activate; python3 -m pytest tests
