# tests/test_maze.py — Tests unitaires de la structure de données Maze.
# Vérifie le bon fonctionnement de la classe Maze, notamment :
#   - la création d'un labyrinthe aux dimensions correctes
#   - l'accès et la modification des murs de chaque cellule
#   - la détection des incohérences entre cellules voisines
#   - la détection des zones ouvertes 3x3 interdites
#   - le placement correct du motif "42" et sa détection
#   - l'encodage hexadécimal de la grille (correspondance bits/directions)
#   - les cas limites : labyrinthe 1x1, dimensions minimales, trop petit pour "42"
