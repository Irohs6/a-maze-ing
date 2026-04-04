# utils/logger.py — Module centralisé de gestion des logs d'erreurs.
# Configure et expose un logger Python (via le module standard logging)
# utilisé par toutes les couches du projet pour tracer les erreurs
# et avertissements.
# Responsabilités :
#   - créer le fichier de log dans logs/maze_errors.txt s'il n'existe pas
#   - formatter les entrées avec horodatage, niveau (ERROR/WARNING/INFO)
#     et message
#   - écrire simultanément dans le fichier de log ET dans la sortie
#     console (stderr)
#   - faire tourner les fichiers de log (RotatingFileHandler) pour éviter
#     que le fichier grossisse indéfiniment
#   - exposer une fonction get_logger(name) retournant un logger nommé
#     prêt à l'emploi pour chaque module qui l'importe
