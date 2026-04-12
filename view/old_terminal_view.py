# view/old_terminal_view.py — Rendu alternatif du labyrinthe (eighth-block).
#
# Génère un labyrinthe 20×20 et l'anime dans un terminal dédié.
# Chaque rangée de cellules occupe UNE seule ligne terminal grâce aux
# caractères ▁ (eighth-block bas, U+2581) : les murs sud sont encodés
# directement dans la ligne de contenu — plus de ligne séparatrice.
#
# Hauteur totale : maze_height + 2 lignes (bordure haute + rangées + bordure basse).
#
# Fonctions :
#   _find_terminal()  : détecte l'émulateur installé (XDG_CURRENT_DESKTOP + which)
#   _open_terminal()  : ouvre une nouvelle fenêtre à la bonne taille
#   _draw_grid()      : affiche la grille initiale (tous murs fermés)
#   _animate()        : anime le perçage des murs en suivant le track
#   _run()            : point d'entrée de l'affichage (génère + dessine + anime)

import os
import shlex
import shutil
import subprocess
import sys
import termios
import time
import tty
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[1]))

from colorama import init, Fore, Style
from model.maze import Maze

# colorama : on gère les resets manuellement pour contrôler les couleurs.
init(autoreset=False)


# ------------------------------------------------------------------
#  ANCIENNE CLASSE (conservée — non utilisée dans __main__)
# ------------------------------------------------------------------


class TerminalView:
    """Ancienne classe de vue terminal (référence uniquement).

    La logique active de rendu a été déplacée dans les fonctions
    de module _draw_grid() et _animate() ci-dessous.
    """

    WALL_N = 1  # mur au nord   (haut)
    WALL_E = 2  # mur à l'est   (droite)
    WALL_S = 4  # mur au sud    (bas)
    WALL_W = 8  # mur à l'ouest (gauche)

    BOX_WALL = " ═║╗══╔╦║╝║╣╚╩╠╬"
    BOX_PATH = " ╴╷┐╶─┌┬╵┘│┤└┴├┼"

    COLORS_42 = [
        ("blanc",          Fore.WHITE),
        ("rouge",          Fore.RED),
        ("vert",           Fore.GREEN),
        ("jaune",          Fore.YELLOW),
        ("bleu",           Fore.BLUE),
        ("magenta",        Fore.MAGENTA),
        ("cyan",           Fore.CYAN),
        ("blanc vif",      Fore.LIGHTWHITE_EX),
        ("rouge vif",      Fore.LIGHTRED_EX),
        ("vert vif",       Fore.LIGHTGREEN_EX),
        ("jaune vif",      Fore.LIGHTYELLOW_EX),
        ("bleu vif",       Fore.LIGHTBLUE_EX),
        ("magenta vif",    Fore.LIGHTMAGENTA_EX),
        ("cyan vif",       Fore.LIGHTCYAN_EX),
        ("bleu vif+gras",  Fore.LIGHTBLUE_EX + Style.BRIGHT),
        ("vert vif+gras",  Fore.LIGHTGREEN_EX + Style.BRIGHT),
        ("rouge vif+gras", Fore.LIGHTRED_EX + Style.BRIGHT),
        ("cyan vif+gras",  Fore.LIGHTCYAN_EX + Style.BRIGHT),
    ]

    # COLOR["42"] est remplacé dynamiquement via [C] dans show_solution.
    COLOR = {
        "wall":   Fore.WHITE,
        "42":     Fore.LIGHTBLUE_EX + Style.BRIGHT,
        "path":   Fore.GREEN,
        "cursor": Fore.GREEN + Style.BRIGHT,
        "entry":  Fore.WHITE,
        "exit":   Fore.RED,
        "info":   Fore.GREEN,
    }
    RESET = Style.RESET_ALL

    def __init__(
        self,
        maze: Maze,
        track: list[Any] | None = None,
        entry: tuple[int, int] = (0, 0),
        exit: tuple[int, int] = (0, 0),
        forty_two_cells: set[tuple[int, int]] | None = None,
        path_connections: dict[tuple[int, int], set[str]] | None = None,
    ) -> None:
        self.maze = maze
        self.track = track
        self.entry = entry
        self.exit_pos = exit
        # Cellules appartenant au motif "42" (murs colorés en bleu).
        self.forty_two: set[tuple[int, int]] = set(forty_two_cells or [])
        # Chemin solution : cellule → directions de connexion (entrée + sortie).
        # Ex : {(2,3): {'N','S'}} = le chemin entre par le nord, repart au sud.
        self.path_connections: dict[tuple[int, int], set[str]] = (
            path_connections or {}
        )
        self._anim_maze = Maze(maze.width, maze.height)

    @staticmethod
    def _read_key() -> str:
        """Lit une touche sans attendre Entrée (mode raw)."""
        file_descriptor = sys.stdin.fileno()
        saved_settings = termios.tcgetattr(file_descriptor)
        try:
            tty.setraw(file_descriptor)
            return sys.stdin.read(1)
        finally:
            termios.tcsetattr(file_descriptor, termios.TCSADRAIN, saved_settings)


# ------------------------------------------------------------------
#  DÉTECTION ET LANCEMENT DU TERMINAL
# ------------------------------------------------------------------


def _find_terminal() -> str | None:
    """Retourne le nom du premier émulateur de terminal installé sur le système.

    Consulte XDG_CURRENT_DESKTOP pour prioriser le terminal natif du bureau
    en cours (GNOME → gnome-terminal, KDE → konsole, etc.), puis vérifie
    que le binaire est réellement présent via shutil.which().

    Note : TERM=xterm-256color est un profil de capacités couleur, pas un
    nom d'exécutable — cette variable ne peut pas servir à la détection.
    """
    desktop_environment = os.environ.get('XDG_CURRENT_DESKTOP', '').lower()

    if 'gnome' in desktop_environment or 'unity' in desktop_environment:
        candidates = ['gnome-terminal', 'xterm']
    elif 'kde' in desktop_environment:
        candidates = ['konsole', 'xterm']
    elif 'xfce' in desktop_environment:
        candidates = ['xfce4-terminal', 'xterm']
    else:
        candidates = ['xterm', 'gnome-terminal', 'konsole',
                      'xfce4-terminal', 'alacritty', 'kitty']

    for terminal_name in candidates:
        if shutil.which(terminal_name):
            return terminal_name
    return None


def _open_terminal(terminal_name: str, columns: int, rows: int) -> bool:
    """Ouvre une nouvelle fenêtre de terminal dimensionnée à
    (columns × rows) chars.

    Passe le flag --spawned au processus enfant pour qu'il sache qu'il tourne
    déjà dans la bonne fenêtre et n'ouvre pas lui-même un autre terminal
    (évite la boucle infinie de spawning).

    Retourne True si le lancement a réussi, False sinon.
    """
    script_path = os.path.abspath(__file__)
    python_executable = sys.executable

    # Commande sous forme de chaîne unique : xfce4-terminal et konsole
    # interprètent -e comme une string shell, pas une liste d'arguments.
    shell_command = (
        f'{shlex.quote(python_executable)} {shlex.quote(script_path)} --spawned'
    )

    # Syntaxe de géométrie et de commande par émulateur :
    #   xterm / alacritty / kitty : arguments séparés après -e
    #   xfce4-terminal / konsole  : chaîne shell unique après -e
    #   gnome-terminal            : arguments séparés après --
    launch_args: dict[str, list[str]] = {
        'xterm': [
            'xterm', '-geometry', f'{columns}x{rows}',
            '-e', python_executable, script_path, '--spawned',
        ],
        'gnome-terminal': [
            'gnome-terminal', f'--geometry={columns}x{rows}',
            '--', python_executable, script_path, '--spawned',
        ],
        'konsole': [
            'konsole', '--geometry', f'{columns}x{rows}',
            '-e', shell_command,
        ],
        'xfce4-terminal': [
            'xfce4-terminal', '--fullscreen',
            '-e', shell_command,
        ],
        'alacritty': [
            'alacritty',
            '--option', f'window.dimensions.columns={columns}',
            '--option', f'window.dimensions.lines={rows}',
            '-e', python_executable, script_path, '--spawned',
        ],
        'kitty': [
            'kitty',
            '--override', f'initial_window_width={columns}c',
            '--override', f'initial_window_height={rows}c',
            python_executable, script_path, '--spawned',
        ],
    }

    args = launch_args.get(terminal_name)
    if args is None:
        return False

    try:
        subprocess.Popen(args)
        return True
    except FileNotFoundError:
        return False


# ------------------------------------------------------------------
#  RENDU ET ANIMATION
# ------------------------------------------------------------------


def _draw_grid(maze_width: int, maze_height: int, cell_width: int) -> None:
    """Affiche la grille initiale du labyrinthe (tous murs fermés).

    Chaque rangée de cellules occupe exactement UNE ligne terminal.
    Les murs sud sont représentés par des ▁ (eighth-block bas, U+2581)
    à l'intérieur de chaque cellule — pas de ligne séparatrice.

    Exemple (cell_width=2, labyrinthe 3×3) :
        ╭──┬──┬──╮   ← bordure haute       (ligne terminal 1)
        │▁▁│▁▁│▁▁│   ← rangée y=0          (ligne terminal 2)
        │▁▁│▁▁│▁▁│   ← rangée y=1          (ligne terminal 3)
        │  │  │  │   ← rangée y=2 (last)   (ligne terminal 4)
        ╰──┴──┴──╯   ← bordure basse       (ligne terminal 5)

    La dernière rangée affiche des espaces au lieu de ▁ car la bordure
    basse joue le rôle de mur sud pour cette rangée.
    """
    horizontal_segment = '─' * cell_width
    south_wall_char = '▁' * cell_width
    empty_cell = ' ' * cell_width

    print('\033c', end='')  # efface l'écran

    # Bordure haute : ╭──────────╮
    for x in range(maze_width):
        if x == 0:
            print('╭' + horizontal_segment + '─', end='')
        elif x < maze_width - 1:
            print(horizontal_segment + '─', end='')
        else:
            print(horizontal_segment + '╮')

    # Rangées de cellules : ▁ pour mur sud présent, espace pour la dernière.
    for y in range(maze_height):
        cell_content = south_wall_char if y < maze_height - 1 else empty_cell
        for x in range(maze_width):
            print('│' + cell_content, end='')
        print('│')

    # Bordure basse : ╰──────────╯
    for x in range(maze_width):
        if x == 0:
            print('╰' + horizontal_segment + '─', end='')
        elif x < maze_width - 1:
            print(horizontal_segment + '─', end='')
        else:
            print(horizontal_segment + '╯')


def _animate(
    track: list[tuple[int, int, str]],
    maze_width: int,
    maze_height: int,
    cell_width: int,
) -> None:
    """Anime la génération en effaçant les murs pas à pas depuis le track.

    Pour chaque étape du track, efface le mur entre la cellule courante et
    sa voisine, puis affiche brièvement un curseur vert ● au centre.

    Correspondance coordonnées → position ANSI (séquences 1-based) :
        terminal_row  = cell_y + 2
            → +1 pour la bordure haute, +1 pour l'indexation 1-based
        terminal_col  = 1 + cell_x × (cell_width + 1)
            → pointe sur le │ gauche de la cellule cell_x
        cursor_column = terminal_col + cell_width // 2
            → centre visuel de la cellule

    Effacement d'un mur selon la direction :
        N → efface ▁ dans la rangée y-1  (mur sud de la cellule au-dessus)
        S → efface ▁ dans la rangée y    (mur sud de la cellule courante)
        E → efface le │ à droite de (x, y)
        W → efface le │ à gauche de (x, y)

    Après chaque affichage du curseur ●, la position est restaurée au
    bon caractère : ▁ si le mur sud est encore intact, espace sinon.
    """
    sys.stdout.write('\033[?25l')  # masque le curseur terminal
    sys.stdout.flush()

    # Murs sud déjà percés — nécessaire pour restaurer le bon caractère
    # après effacement du ● : le curseur écrase le ▁ à sa position, et
    # sans restauration ce ▁ disparaît définitivement.
    open_south_walls: set[tuple[int, int]] = set()

    for cell_x, cell_y, direction in track:
        time.sleep(0.05)

        terminal_row = cell_y + 2
        terminal_col = 1 + cell_x * (cell_width + 1)
        cursor_column = terminal_col + max(1, cell_width // 2)

        if direction == 'N':
            # Perce le mur sud de la cellule au-dessus (cell_x, cell_y - 1).
            sys.stdout.write(
                f'\033[{cell_y + 1};{terminal_col + 1}H{" " * cell_width}'
            )
            open_south_walls.add((cell_x, cell_y - 1))
        elif direction == 'S':
            # Perce le mur sud de la cellule courante (cell_x, cell_y).
            sys.stdout.write(
                f'\033[{terminal_row};{terminal_col + 1}H{" " * cell_width}'
            )
            open_south_walls.add((cell_x, cell_y))
        elif direction == 'E':
            wall_column = terminal_col + cell_width + 1
            sys.stdout.write(f'\033[{terminal_row};{wall_column}H ')
        elif direction == 'W':
            wall_column = terminal_col
            sys.stdout.write(f'\033[{terminal_row};{wall_column}H ')

        sys.stdout.write(
            f'\033[{terminal_row};{cursor_column}H'
            f'{Fore.GREEN}●{Style.RESET_ALL}'
        )
        sys.stdout.flush()

        # Restaure ▁ si le mur sud est encore intact, espace s'il est percé
        # ou si c'est la dernière rangée (pas de mur sud, bordure à la place).
        south_is_open = (cell_x, cell_y) in open_south_walls
        is_last_row = cell_y == maze_height - 1
        restored_char = ' ' if south_is_open or is_last_row else '▁'
        sys.stdout.write(f'\033[{terminal_row};{cursor_column}H{restored_char}')

    sys.stdout.write(f'\033[{maze_height + 3};1H')
    sys.stdout.write('\033[?25h')  # restaure le curseur terminal
    sys.stdout.flush()
    input('\nAppuie sur Entrée pour quitter…')


def _run(cell_width: int) -> None:
    """Génère le labyrinthe et lance l'affichage complet (grille + animation)."""
    from mazegen.maze_generator import MazeGenerator

    generator = MazeGenerator(width=20, height=20, seed=42, perfect=False)
    generator.generate()
    # get_maze() retourne le labyrinthe interne de MazeGenerator.
    # Créer Maze(20, 20) séparément donnerait une grille vide (tous murs fermés).
    maze = generator.get_maze()

    _draw_grid(maze.width, maze.height, cell_width)
    _animate(generator.track, maze.width, maze.height, cell_width)


# ------------------------------------------------------------------
#  POINT D'ENTRÉE
# ------------------------------------------------------------------

if __name__ == '__main__':
    # cell_width=2 → rendu carré avec le mode eighth-block.
    # Chaque cellule fait cell_width × 8 px de large et 16 px de haut.
    # Pour un carré : 2 × 8 = 16  →  cell_width = 2.
    CELL_WIDTH = 2
    MAZE_WIDTH = 20
    MAZE_HEIGHT = 20

    # needed_columns = (cell_width + 1) × maze_width + 1  =  3 × 20 + 1  =  61
    # needed_rows    = maze_height + 2 + 1                = 20 + 2 + 1   =  23
    needed_columns = (CELL_WIDTH + 1) * MAZE_WIDTH + 1
    needed_rows = MAZE_HEIGHT + 2 + 1

    # --spawned : ce processus tourne déjà dans
    # la bonne fenêtre → affichage direct.
    # Sans ce flag : on ouvre un nouveau terminal — évite la boucle infinie.
    if '--spawned' in sys.argv:
        _run(CELL_WIDTH)
    else:
        terminal_name = _find_terminal()
        if terminal_name and _open_terminal(terminal_name, needed_columns, needed_rows):
            print(f'Ouverture dans {terminal_name}…')
        else:
            _run(CELL_WIDTH)
