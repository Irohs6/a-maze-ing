# tests/test_path_finder.py — Tests unitaires de l'algorithme de recherche de chemin.
# Vérifie le comportement de PathFinder sur différents labyrinthes de test :
#   - chemin trouvé sur un labyrinthe simple avec solution évidente
#   - chemin le plus court retourné (pas un chemin quelconque)
#   - labyrinthe parfait : un seul chemin possible, correctement détecté
#   - labyrinthe non connexe : détection de cellules inaccessibles
#   - validation du format de sortie du chemin (lettres N, E, S, O uniquement)
#   - reproductibilité : même graine donne même chemin solution
