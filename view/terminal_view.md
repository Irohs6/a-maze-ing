# view/terminal_view.py

## Rôle
Vue principale du labyrinthe dans le terminal. Gère l'affichage coloré avec des caractères Unicode box-drawing, l'animation de génération et la visualisation du chemin solution.

## Ce qu'il fait
- Dessine le labyrinthe en utilisant des caractères de bordure double (`╔╗╚╝╬…`) pour les murs et simple (`┌┐└┘┼…`) pour le chemin
- Affiche le motif "42" dans une couleur distincte (configurable via `[C]`)
- Anime la génération cellule par cellule depuis le `track` fourni par l'algorithme
- Affiche la solution (chemin BFS) par-dessus le labyrinthe
- Gère la saisie clavier en mode raw (`termios`/`tty`) pour des interactions immédiates
- Supporte le cycle de couleurs de 42 (`COLORS_42`) avec la touche `[C]`
- Sauvegarde le labyrinthe encodé en hex dans le fichier de sortie

## Note globale : 8/10

## Améliorations possibles
| Priorité | Amélioration |
|----------|-------------|
| Haute | Fichier très long — bénéficierait d'être splitté en `renderer.py` (dessin) + `animator.py` (animation) + `input_handler.py` (clavier) |
| Haute | La gestion du terminal raw (`termios`) n'est pas protégée dans un `try/finally` systématique — risque de laisser le terminal en état raw en cas d'exception |
| Moyenne | Les constantes `BOX_WALL` et `BOX_PATH` sont des lookup tables indexées par bitmask — ajouter un commentaire explicatif de la technique |
| Faible | La vitesse d'animation est fixe — exposer un paramètre `speed` configurable |
