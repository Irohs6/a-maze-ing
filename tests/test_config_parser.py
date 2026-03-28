# tests/test_config_parser.py — Tests unitaires du parseur de configuration.
# Couvre tous les scénarios de lecture et de validation du fichier config :
#   - fichier valide avec toutes les clés obligatoires
#   - fichier avec commentaires et lignes vides (doivent être ignorés)
#   - clés obligatoires manquantes (doit lever une exception)
#   - valeurs de types incorrects (ex. : WIDTH=abc)
#   - coordonnées hors limites du labyrinthe
#   - fichier inexistant ou chemin invalide
#   - clés optionnelles absentes (vérification des valeurs par défaut)
