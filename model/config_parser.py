# model/config_parser.py — Parseur du fichier de configuration.
# Contient la classe ConfigParser responsable de lire et valider le fichier config.
# Elle gère :
#   - la lecture ligne par ligne en ignorant les commentaires (#)
#   - l'extraction des paires CLE=VALEUR
#   - la validation de la présence de toutes les clés obligatoires
#   - la conversion et la validation des types (entiers, booléen, coordonnées)
#   - la vérification que les coordonnées d'entrée/sortie sont dans les limites du labyrinthe
#   - les clés optionnelles (SEED, ALGORITHM) avec leurs valeurs par défaut
# Lève des exceptions descriptives pour chaque type d'erreur rencontré.
