# Makefile — Automatisation des tâches courantes du projet.
# Contient les règles obligatoires suivantes :
#   install  : installe les dépendances Python listées dans requirements.txt
#   run      : lance le programme principal avec le fichier config.txt par défaut
#   debug    : lance le programme en mode débogage via pdb
#   clean    : supprime les caches Python (__pycache__, .mypy_cache, .pytest_cache)
#   lint     : exécute flake8 et mypy avec les flags obligatoires du sujet
#   lint-strict : exécute flake8 et mypy en mode strict (optionnel mais recommandé)
# Peut également contenir une règle 'test' pour lancer la suite pytest.
