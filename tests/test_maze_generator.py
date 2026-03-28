# tests/test_maze_generator.py — Tests unitaires du module réutilisable MazeGenerator.
# Valide l'API publique exposée par le paquet mazegen :
#   - instanciation avec différentes combinaisons de paramètres
#   - génération déterministe : même seed produit toujours le même labyrinthe
#   - get_maze() retourne une structure 2D cohérente aux bonnes dimensions
#   - get_solution() retourne un chemin valide reliant l'entrée à la sortie
#   - mode parfait : vérification qu'un seul chemin existe entre entrée et sortie
#   - reset() régénère correctement avec une nouvelle graine
#   - gestion des paramètres invalides (dimensions négatives, seed non entier, etc.)
