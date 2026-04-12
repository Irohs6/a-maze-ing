# view/terminal_view.py

## Rôle
Vue principale du labyrinthe dans le terminal. Gère l'affichage coloré avec des caractères Unicode box-drawing, l'animation de génération et la visualisation interactive de la solution.

## Ce qu'il fait
- Dessine le labyrinthe en utilisant des caractères de bordure double (`╔╗╚╝╬…`) pour les murs et simple (`┌┐└┘┼…`) pour le chemin — lookup tables `BOX_WALL` / `BOX_PATH` indexées par bitmask de 4 bits (gauche/bas/droite/haut)
- S'adapte à la largeur du terminal : mode normal (3 chars/cellule) ou compact (1 char/cellule) via `_compute_scale()`
- Si le terminal est trop petit, désactive l'animation ANSI et fait un rendu statique final
- Affiche le motif "42" dans une couleur distincte (configurable cycle via `[C]`, 18 couleurs disponibles dans `COLORS_42`)
- **Animation** (`play()`) : dessine le labyrinthe vide une seule fois, puis met à jour uniquement les cellules et segments modifiés via ANSI (positionnement curseur `\033[row;colH`)
- **Solution interactive** (`show_solution()`) :
  - Appelle `play()` pour l'animation de génération, puis entre en boucle de lecture clavier
  - `[S]` : affiche / cache la solution
  - `[C]` : cycle de couleurs du motif 42
  - `[N]` / `[P]` : chemin suivant / précédent (labyrinthes imparfaits)
  - `[Q]` : quitter
  - Indique si le labyrinthe est parfait (chemin unique) ou imparfait (plusieurs chemins)
- Lecture clavier en mode raw (`termios`/`tty`) via `_read_key()` — restaure le terminal dans un `try/finally`
- L'écriture dans le fichier de sortie est gérée par `Menu._execute()`, pas par cette classe

## Note globale : 9/10

## Aspect ratio des caractères terminal

Les polices monospace de terminal utilisent des cellules d'environ **8×16 px** (ratio largeur:hauteur ≈ 1:2), héritage des terminaux CRT des années 70-80 (ex. VT100 : 640×480 px → 80×24 chars → 8×20 px/char).

Conséquence pour le rendu du labyrinthe :
- Un labyrinthe N×N avec 3 chars/cellule produit `(3N+1)` colonnes et `(2N+1)` lignes
- Visuellement : largeur = `(3N+1) × 1` unités, hauteur = `(2N+1) × 2` unités → **plus haut que large**
- Pour un carré visuel parfait, il faut **4 chars/cellule en largeur** :
  - Largeur : `(4N+1) × 1 ≈ (2N+1) × 2` : Hauteur → ratio ~1:1

C'est pourquoi `_compute_scale()` choisit entre 3 chars/cellule (normal) et 1 char/cellule (compact), mais aucun des deux ne produit un carré visuel parfait. La valeur idéale serait **4 chars/cellule**.

## Améliorations possibles
| Priorité | Amélioration |
|----------|-------------|
| Haute | Fichier très long (~550 lignes) — bénéficierait d'être splitté en `renderer.py` (dessin) + `animator.py` (animation) + `input_handler.py` (clavier) |
| Moyenne | `_render()` reconstruit toute la chaîne en mémoire avant d'imprimer — sur très grands labyrinthes, consommation mémoire non négligeable |
| Faible | La vitesse d'animation est fixe (`delay=0.001s`) — exposer un paramètre `speed` configurable |
| Faible | `COLORS_42` est une liste de tuples (nom, code) non typée — remplacer par un `NamedTuple` ou dataclass pour la clarté |
