# view/terminal_view.py — Rendu ASCII du labyrinthe dans le terminal.
# Contient la classe TerminalView responsable de l'affichage en mode texte.
# Elle lit la structure d'un objet Maze et construit une représentation ASCII
# avec des caractères pour les murs (ex. : +, -, |) et les espaces pour les passages.
# Gère l'affichage de :
#   - l'entrée et la sortie avec des marqueurs distincts
#   - le chemin solution (affiché ou masqué à la demande)
#   - les couleurs des murs via les codes ANSI
#   - le motif "42" avec une couleur optionnelle différente
# Implémente les interactions utilisateur en mode terminal :
#   touche 'r' pour régénérer, 's' pour afficher/masquer la solution, 'c' pour changer les couleurs.
