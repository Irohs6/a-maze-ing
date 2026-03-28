# model/maze.py — Structure de données représentant le labyrinthe.
# Contient la classe Maze qui stocke la grille de cellules et leurs murs.
# Chaque cellule est représentée par un entier sur 4 bits (Nord, Est, Sud, Ouest).
# La classe fournit des méthodes pour :
#   - accéder et modifier les murs d'une cellule donnée
#   - vérifier la validité des données (cohérence des murs entre cellules voisines)
#   - détecter les zones ouvertes interdites (aucune zone 3x3 sans murs)
#   - encoder le labyrinthe en hexadécimal pour l'écriture dans le fichier de sortie
#   - placer et vérifier le motif "42" dans la grille
# Utilise des annotations de type et des docstrings conformes à PEP 257.
