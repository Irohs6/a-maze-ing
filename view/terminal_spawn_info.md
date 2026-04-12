# Rendu terminal : techniques appliquées dans `old_terminal_view.py`

Ce document explique les problèmes concrets rencontrés lors de l'affichage
animé d'un labyrinthe dans un terminal, les solutions retenues, et comment
elles fonctionnent techniquement.

---

## 1. Pourquoi les caractères forment un rectangle, pas un carré

### Le problème

Un labyrinthe 20×20 affiché naïvement (1 char/cellule) occupe 20 colonnes
pour 20 lignes. Visuellement le résultat est un rectangle allongé verticalement.

### La cause : l'aspect ratio des polices monospace

Les polices monospace utilisées dans les terminaux héritent du matériel
historique. Les terminaux VT100 des années 80 avaient des CRT de 640×480 px
affichant 80×24 caractères, soit des cellules de 8×20 px — un ratio largeur:hauteur
de **1:2.5**. Les polices modernes restent dans cette tradition : une cellule
fait environ **8×16 px** (ratio **1:2**).

### La solution : `cell_w = 4`

Pour que chaque cellule paraisse carrée à l'écran, il faut compenser le ratio
en largeur :

```
cellule visuelle carrée (16×16 px)  =  4 chars × 8 px  par  1 char × 16 px
                                              ↕                     ↕
                                           largeur               hauteur
```

Formule des dimensions nécessaires pour un labyrinthe `W×H` avec `cell_w=4` :

```
cols_needed = cell_w × W + 1  =  4 × 20 + 1  =  81 colonnes
rows_needed = 2 × H + 3       =  2 × 20 + 3  =  43 lignes
```

(+3 : bordure haute, bordure basse, ligne de status)

---

## 2. Pourquoi le positionnement ANSI casse quand le terminal est trop petit

### Ce que fait `\033[row;colH`

La séquence d'échappement ANSI `\033[row;colH` (CSI CUP — Cursor Position)
déplace le curseur à une position **absolue** depuis le coin supérieur gauche
de l'écran visible. Elle ne connaît pas le contenu déjà affiché.

### Le bug de scroll

Si le labyrinthe fait 43 lignes mais que le terminal n'en montre que 24, le
terminal scrolle dès que l'affichage initial atteint la ligne 24. Résultat :
la ligne 1 de l'affichage se retrouve en dehors de la zone visible, et toutes
les coordonnées absolues pointent vers les mauvaises lignes de la grille.
L'animation écrit des curseurs au mauvais endroit — le labyrinthe est corrompu
visuellement.

### Pourquoi ne pas simplement détecter et désactiver l'animation ?

Une solution simple serait d'afficher statiquement quand le terminal est trop
petit. Mais cela perd tout l'intérêt de la vue animée. La vraie solution est
de **garantir** que le terminal a exactement la taille requise avant de lancer
l'animation — d'où l'approche par spawn.

---

## 3. Solution retenue : ouvrir un nouveau terminal à la bonne taille

### Principe

Au lieu d'adapter l'affichage au terminal courant, on ouvre une **nouvelle
fenêtre de terminal** avec la taille exacte nécessaire (81×43), et on y lance
le script. La bonne taille est garantie, pas approximée.

```
script (terminal courant)
    │
    ├─ calcule cols_needed=81, rows_needed=43
    ├─ détecte le terminal disponible (ex: xterm)
    └─ subprocess.Popen(['xterm', '-geometry', '81x43', '-e', 'python3 script.py --spawned'])
                                                                         │
                                                        nouveau terminal │
                                                        81×43 colonnes   │
                                                        lance le script ─┘
```

### Le flag `--spawned`

Sans protection, le nouveau terminal relancerait un autre terminal, qui en
relancerait un autre, et ainsi de suite (boucle infinie).

Le flag `--spawned` dans `sys.argv` indique que le script tourne déjà dans la
fenêtre correcte — il doit afficher directement sans respawner.

```python
if '--spawned' in sys.argv:
    _run_maze(CELL_W)          # on est dans la bonne fenêtre → on affiche
else:
    terminal = _find_terminal()
    if terminal:
        _spawn_in_terminal(...)    # on ouvre une nouvelle fenêtre
```

---

## 4. Détection du terminal disponible : `XDG_CURRENT_DESKTOP` + `shutil.which()`

### Pourquoi `TERM` est inutilisable

```bash
echo $TERM   # → "xterm-256color"
```

`TERM` est un **profil de capacités** (définit quelles séquences ANSI sont
supportées), pas le nom de l'émulateur installé. La valeur `xterm-256color`
est couramment définie par gnome-terminal, xfce4-terminal, kitty, alacritty…
Utiliser `TERM` pour trouver l'exécutable serait toujours faux.

### Pourquoi `TERM_PROGRAM` est insuffisant

`TERM_PROGRAM` est correctement renseigné sur macOS (iTerm2, Terminal.app)
mais **rarement défini sur Linux**. Inutilisable comme solution principale.

### Pourquoi lire `/proc/$PPID/comm` ne marche pas

```bash
cat /proc/$PPID/comm   # → "zsh" ou "bash"
```

`$PPID` est le PID du **shell parent** (zsh, bash…), pas du terminal émulateur.
Le terminal emulator est encore un niveau au-dessus dans l'arbre de processus —
naviguer cet arbre est fragile et non portable.

### Solution : `XDG_CURRENT_DESKTOP` + `shutil.which()`

```python
desktop = os.environ.get('XDG_CURRENT_DESKTOP', '').lower()
# → "gnome", "kde", "xfce", "unity", ""...
```

`XDG_CURRENT_DESKTOP` donne le bureau en cours (GNOME, KDE, XFCE…), ce qui
permet de **prioriser** le terminal natif du bureau. Puis `shutil.which(t)`
vérifie qu'il est effectivement installé en cherchant le binaire dans `$PATH`.

```python
if 'gnome' in desktop:
    preferred = ['gnome-terminal', 'xterm']
elif 'kde' in desktop:
    preferred = ['konsole', 'xterm']
elif 'xfce' in desktop:
    preferred = ['xfce4-terminal', 'xterm']
else:
    preferred = ['xterm', 'gnome-terminal', 'konsole', 'xfce4-terminal',
                 'alacritty', 'kitty']

for t in preferred:
    if shutil.which(t):   # cherche le binaire dans $PATH
        return t
```

`shutil.which()` est la méthode standard Python pour vérifier l'existence
d'un exécutable — équivalent de `command -v` en bash.

---

## 5. Syntaxe de géométrie par émulateur

Chaque terminal a sa propre façon de définir la taille initiale de la fenêtre.
Aucune syntaxe n'est universelle :

| Terminal        | Argument de géométrie                          | Séparateur commande |
|-----------------|------------------------------------------------|---------------------|
| xterm           | `-geometry 81x43`                              | `-e cmd`            |
| gnome-terminal  | `--geometry=81x43`                             | `-- cmd args`       |
| konsole         | `--geometry 81x43`                             | `-e cmd`            |
| xfce4-terminal  | `--geometry=81x43`                             | `-e cmd`            |
| alacritty       | `--option window.dimensions.columns=81 --option window.dimensions.lines=43` | `-e cmd args` |
| kitty           | `--override initial_window_width=81c --override initial_window_height=43c` | `cmd args` |

Le suffixe `c` pour alacritty/kitty signifie "en colonnes/lignes" (vs pixels).

---

## 6. Fallback si aucun terminal n'est disponible

Si `_find_terminal()` retourne `None` (aucun terminal externe installé, ou
environnement headless/CI), le script tourne dans le terminal courant.

Si le terminal est trop petit, un avertissement est affiché mais l'animation
se lance quand même — dans ce contexte there's nothing better we can do.

```python
cols, rows = shutil.get_terminal_size()
if rows < needed_rows:
    print(f"\033[33m⚠ Terminal {cols}×{rows} trop petit …\033[0m")
_run_maze(CELL_W)
```

---

## Résumé des choix

| Problème                        | Solution appliquée                        | Raison du choix                             |
|---------------------------------|-------------------------------------------|---------------------------------------------|
| Rendu rectangle au lieu de carré| `cell_w = 4` (4 chars/cellule en largeur) | Compense ratio 1:2 des polices monospace    |
| Animation ANSI cassée si scroll | Ouvrir un nouveau terminal à taille fixe  | Garantit la taille, pas d'approximation     |
| Trouver l'émulateur installé    | `XDG_CURRENT_DESKTOP` + `shutil.which()`  | TERM et TERM_PROGRAM sont fiables uniquement sur macOS |
| Boucle infinie de spawn         | Flag `--spawned` dans sys.argv            | Simple et robuste, pas besoin de fichier PID |
| Pas de terminal externe         | Fallback avec avertissement               | Environnements headless/CI doivent fonctionner |

---

## Glossaire des variables et fonctions

Ce glossaire explique le rôle de chaque variable et fonction du fichier
`view/old_terminal_view.py`, dans l'ordre où elles apparaissent.

### Constantes du point d'entrée (`__main__`)

| Variable          | Type  | Valeur | Rôle                                                         |
|-------------------|-------|--------|--------------------------------------------------------------|
| `CELL_WIDTH`      | `int` | `2`    | Largeur d'une cellule en nombre de caractères. Vaut 2 pour un rendu carré (2×8px = 16px = hauteur d'une ligne). |
| `MAZE_WIDTH`      | `int` | `20`   | Largeur du labyrinthe en nombre de cellules.                 |
| `MAZE_HEIGHT`     | `int` | `20`   | Hauteur du labyrinthe en nombre de cellules.                 |
| `needed_columns`  | `int` | `61`   | Colonnes de terminal nécessaires : `(CELL_WIDTH + 1) × MAZE_WIDTH + 1`. |
| `needed_rows`     | `int` | `23`   | Lignes de terminal nécessaires : `MAZE_HEIGHT + 2 + 1` (bordures + status). |

### `_find_terminal()`

| Variable               | Type        | Rôle                                                      |
|------------------------|-------------|-----------------------------------------------------------|
| `desktop_environment`  | `str`       | Valeur de `XDG_CURRENT_DESKTOP` en minuscules. Exemple : `"xfce"`, `"gnome"`, `""`. |
| `candidates`           | `list[str]` | Liste ordonnée d'émulateurs à tester (natif du bureau en priorité). |
| `terminal_name`        | `str`       | Nom d'un émulateur testé dans la boucle (`'xterm'`, `'konsole'`, etc.). |

### `_open_terminal(terminal_name, columns, rows)`

| Variable              | Type               | Rôle                                                         |
|-----------------------|--------------------|--------------------------------------------------------------|
| `terminal_name`       | `str`              | Nom de l'émulateur retourné par `_find_terminal()`.          |
| `columns`             | `int`              | Largeur souhaitée de la fenêtre en colonnes de caractères.   |
| `rows`                | `int`              | Hauteur souhaitée de la fenêtre en lignes de caractères.     |
| `script_path`         | `str`              | Chemin absolu vers ce fichier (`os.path.abspath(__file__)`). |
| `python_executable`   | `str`              | Chemin vers l'interpréteur Python courant (`sys.executable`). Garantit que le bon Python est utilisé même dans un venv. |
| `shell_command`       | `str`              | Commande sous forme de chaîne unique pour les émulateurs qui l'exigent (`xfce4-terminal -e`). Les chemins sont protégés par `shlex.quote()`. |
| `launch_args`         | `dict[str, list]`  | Dictionnaire émulateur → liste d'arguments `subprocess.Popen`. Chaque émulateur a sa propre syntaxe pour la géométrie. |
| `args`                | `list[str] \| None`| Arguments sélectionnés pour l'émulateur demandé. `None` si l'émulateur est inconnu. |

### `_draw_grid(maze_width, maze_height, cell_width)`

| Variable             | Type  | Rôle                                                              |
|----------------------|-------|-------------------------------------------------------------------|
| `maze_width`         | `int` | Nombre de cellules en largeur.                                    |
| `maze_height`        | `int` | Nombre de cellules en hauteur.                                    |
| `cell_width`         | `int` | Largeur d'une cellule en caractères (sans les murs `│`).          |
| `horizontal_segment` | `str` | Séquence `'─' × cell_width`. Remplit le dessus/dessous d'une cellule. |
| `south_wall_char`    | `str` | Séquence `'▁' × cell_width`. Représente un mur sud présent.      |
| `empty_cell`         | `str` | Séquence `' ' × cell_width`. Utilisée pour la dernière rangée (pas de mur sud visible). |
| `cell_content`       | `str` | Vaut `south_wall_char` ou `empty_cell` selon la rangée `y`.      |

### `_animate(track, maze_width, maze_height, cell_width)`

| Variable          | Type                       | Rôle                                                              |
|-------------------|----------------------------|-------------------------------------------------------------------|
| `track`           | `list[tuple[int,int,str]]` | Séquence des murs percés : `(cell_x, cell_y, direction)`.        |
| `open_south_walls`| `set[tuple[int,int]]`      | Ensemble des cellules dont le mur sud a déjà été percé. Sert à restaurer le bon caractère (`▁` ou `' '`) après effacement du curseur `●`. |
| `cell_x`, `cell_y`| `int`                      | Coordonnées de la cellule courante dans la grille (0-based).      |
| `direction`       | `str`                      | Direction du mur percé : `'N'`, `'S'`, `'E'` ou `'W'`.          |
| `terminal_row`    | `int`                      | Ligne ANSI (1-based) de la rangée `cell_y` : `cell_y + 2`.       |
| `terminal_col`    | `int`                      | Colonne ANSI (1-based) du `│` gauche de la cellule `cell_x` : `1 + cell_x × (cell_width + 1)`. |
| `cursor_column`   | `int`                      | Colonne ANSI du centre visuel de la cellule (position du `●`) : `terminal_col + cell_width // 2`. |
| `south_is_open`   | `bool`                     | `True` si le mur sud de la cellule courante a déjà été percé.    |
| `is_last_row`     | `bool`                     | `True` si la cellule est sur la dernière rangée (mur sud = bordure basse). |
| `restored_char`   | `str`                      | Caractère à remettre après effacement du `●` : `' '` si le mur est ouvert ou absent, `'▁'` sinon. |

### `_run(cell_width)`

| Variable    | Type           | Rôle                                                               |
|-------------|----------------|--------------------------------------------------------------------|
| `generator` | `MazeGenerator`| Génère le labyrinthe (seed fixe pour reproductibilité).           |
| `maze`      | `Maze`         | Labyrinthe interne récupéré via `generator.get_maze()`. Créer `Maze(20, 20)` séparément produirait une grille vide. |

