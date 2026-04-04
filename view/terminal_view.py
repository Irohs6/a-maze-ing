# view/terminal_view.py

import os
import sys
import termios
import time
import tty
from typing import Any

from colorama import init, Fore, Style
from model.maze import Maze

init(autoreset=False)


class TerminalView:
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
        # Coordinates (x, y) of the cells belonging to the 42 pattern.
        # Stored as a set for fast membership checks.
        self.forty_two_cells: set[tuple[int, int]] = set(forty_two_cells or [])
        # Per-cell path directions: maps (x, y) to the set of directions
        # the solution path connects through that cell.
        self.path_connections: dict[tuple[int, int], set[str]] = (
            path_connections or {}
        )
        # Maze vierge dédié à l'animation — les murs sont cassés au fur et
        # à mesure du track pour que la progression reste 100 % visible.
        self._anim_maze = Maze(maze.width, maze.height)

    # ---------------------------------------------------------
    #  HELPERS STATIQUES
    # ---------------------------------------------------------

    @staticmethod
    def _getch() -> str:
        """Read a single keypress without requiring Enter."""
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            return sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)

    @staticmethod
    def _dirs_to_connections(
        path_dirs: list[str], start: tuple[int, int]
    ) -> dict[tuple[int, int], set[str]]:
        """Convert a list of directions to per-cell connection sets."""
        OFFSETS = {'N': (0, -1), 'E': (1, 0), 'S': (0, 1), 'W': (-1, 0)}
        REVERSE = {'N': 'S', 'S': 'N', 'E': 'W', 'W': 'E'}
        connections: dict[tuple[int, int], set[str]] = {}
        x, y = start
        connections[(x, y)] = set()
        for d in path_dirs:
            connections[(x, y)].add(d)
            dx, dy = OFFSETS[d]
            x, y = x + dx, y + dy
            if (x, y) not in connections:
                connections[(x, y)] = set()
            connections[(x, y)].add(REVERSE[d])
        return connections

    PALETTE_MATRIX: dict[str, str] = {
        "wall": Fore.WHITE,
        "empty": Style.RESET_ALL,
        "entry": Fore.WHITE,
        "exit": Fore.RED,
        "cursor": Fore.GREEN + Style.BRIGHT,
        "path": Fore.GREEN,
        "forty_two": Fore.RED + Style.BRIGHT,
        "info": Fore.GREEN,
    }

    # ---------------------------------------------------------
    #  ANIMATION DE LA GÉNÉRATION
    # ---------------------------------------------------------

    def play(self, delay: float = 0.03) -> None:
        if not self.track:
            return

        directions = {
            'N': (0, -1),
            'E': (1, 0),
            'S': (0, 1),
            'W': (-1, 0),
        }

        pos_stack = [(0, 0)]
        anim = self._anim_maze

        for step in self.track:
            os.system("clear")

            if step != "BACK":
                x, y = pos_stack[-1]
                dx, dy = directions[step]
                nx, ny = x + dx, y + dy
                anim.remove_wall(x, y, step)
                pos_stack.append((nx, ny))
            else:
                # Empêcher la pile de devenir vide
                if len(pos_stack) > 1:
                    pos_stack.pop()

            self._print_with_cursor(pos_stack[-1], anim)
            print(f"\nStep: {step}")

            time.sleep(delay)

    def play_kruksal(self, delay: float = 0.03) -> None:
        if not self.track:
            return
        anim = self._anim_maze

        for step in self.track:
            os.system("clear")
            anim.remove_wall(*step)
            self._print_with_cursor((step[0], step[1]), anim)
            print(f"\nStep: {step[2]}")

            time.sleep(delay)

    # ---------------------------------------------------------
    #  AFFICHAGE AVEC CURSEUR
    # ---------------------------------------------------------
    def _print_with_cursor(
        self, cursor_pos: tuple[int, int], maze: Maze | None = None
    ) -> None:
        if maze is None:
            maze = self.maze
        h = maze.height
        w = maze.width
        grid = maze.grid

        cx, cy = cursor_pos
        ex, ey = self.entry
        sx, sy = self.exit_pos

        BOX = " ╴╷┐╶─┌┬╵┘│┤└┴├┼"

        def h_seg(x: int, iy: int) -> bool:
            if iy < h and grid[iy][x] & 1:
                return True
            if iy > 0 and grid[iy - 1][x] & 4:
                return True
            return False

        def v_seg(ix: int, y: int) -> bool:
            if ix < w and grid[y][ix] & 8:
                return True
            if ix > 0 and grid[y][ix - 1] & 2:
                return True
            return False

        P = self.PALETTE_MATRIX
        WALL = P["wall"]
        RESET = Style.RESET_ALL
        FORTY_TWO_WALL = P["forty_two"]
        ENTRY_ICON = "🚀 "
        EXIT_ICON = "🏁 "

        forty_two = self.forty_two_cells

        def is_42_cell(x: int, y: int) -> bool:
            return (x, y) in forty_two

        def h_wall_color(x: int, iy: int) -> str:
            """Color for the horizontal wall at (x, iy) if it exists."""
            blue = False
            if iy < h and (grid[iy][x] & 1) and is_42_cell(x, iy):
                blue = True
            if iy > 0 and (grid[iy - 1][x] & 4) and is_42_cell(x, iy - 1):
                blue = True
            return FORTY_TWO_WALL if blue else WALL

        def v_wall_color(ix: int, y: int) -> str:
            """Color for the vertical wall at (ix, y) if it exists."""
            blue = False
            if ix < w and (grid[y][ix] & 8) and is_42_cell(ix, y):
                blue = True
            if ix > 0 and (grid[y][ix - 1] & 2) and is_42_cell(ix - 1, y):
                blue = True
            return FORTY_TWO_WALL if blue else WALL

        def junction_color(ix: int, iy: int, up: bool,
                           down: bool, left: bool, right: bool) -> str:
            """Color for the junction char at grid intersection (ix, iy)."""
            blue = False
            if left and ix > 0 and iy <= h:
                blue = blue or (h_wall_color(ix - 1, iy) == FORTY_TWO_WALL)
            if right and ix < w and iy <= h:
                blue = blue or (h_wall_color(ix, iy) == FORTY_TWO_WALL)
            if up and iy > 0 and ix <= w:
                # up segment is v_seg(ix, iy-1)
                if (iy - 1) < h:
                    blue = blue or (v_wall_color(ix, iy - 1) == FORTY_TWO_WALL)
            if down and iy < h and ix <= w:
                blue = blue or (v_wall_color(ix, iy) == FORTY_TWO_WALL)
            return FORTY_TWO_WALL if blue else WALL

        for iy in range(h + 1):
            top = ""
            for ix in range(w + 1):
                up = iy > 0 and v_seg(ix, iy - 1)
                down = iy < h and v_seg(ix, iy)
                left = ix > 0 and h_seg(ix - 1, iy)
                right = ix < w and h_seg(ix, iy)
                box_idx = (
                    int(left)
                    + int(down) * 2
                    + int(right) * 4
                    + int(up) * 8
                )
                top += (
                    junction_color(ix, iy, up, down, left, right)
                    + BOX[box_idx]
                    + RESET
                )
                if ix < w:
                    top += (
                        (h_wall_color(ix, iy) + "───" + RESET)
                        if h_seg(ix, iy)
                        else "   "
                    )
            print(top)

            if iy < h:
                mid = ""
                for ix in range(w + 1):
                    mid += (
                        (v_wall_color(ix, iy) + "│" + RESET)
                        if v_seg(ix, iy)
                        else " "
                    )
                    if ix < w:
                        if (ix, iy) == (cx, cy):
                            mid += P["cursor"] + " ● " + RESET
                        elif (ix, iy) == (ex, ey):
                            mid += P["entry"] + ENTRY_ICON + RESET
                        elif (ix, iy) == (sx, sy):
                            mid += P["exit"] + EXIT_ICON + RESET
                        else:
                            mid += "   "
                print(mid)

    # ---------------------------------------------------------
    #  AFFICHAGE INTERACTIF DE LA SOLUTION
    # ---------------------------------------------------------

    def show_solution(
        self, all_paths: list[list[str]], is_perfect: bool
    ) -> None:
        """Display the maze with solution path and allow switching if imperfect.

        Keys: [N] next path, [P] previous path (imperfect only), [Q] quit.
        """
        P = self.PALETTE_MATRIX
        RESET = Style.RESET_ALL
        current = 0
        total = len(all_paths)

        while True:
            self.path_connections = self._dirs_to_connections(
                all_paths[current], self.entry
            )
            os.system("clear")
            self.print_unicode()

            if is_perfect:
                print(
                    f"\n{P['info']}✓ Labyrinthe parfait généré"
                    f" (chemin unique){RESET}"
                )
                print("  [Q] quitter")
            else:
                print(
                    f"\n{Fore.YELLOW}⚠ Labyrinthe imparfait généré"
                    f" — chemin {current + 1}/{total}{RESET}"
                )
                print(
                    "  [N] prochain chemin  "
                    "[P] chemin précédent  [Q] quitter"
                )

            key = self._getch().lower()
            if key == 'q':
                break
            if not is_perfect:
                if key == 'n':
                    current = (current + 1) % total
                elif key == 'p':
                    current = (current - 1) % total

    # ---------------------------------------------------------
    #  AFFICHAGE FINAL
    # ---------------------------------------------------------
    def print_unicode(self) -> None:
        maze = self.maze
        h = maze.height
        w = maze.width
        grid = maze.grid

        ex, ey = getattr(self, 'entry', (0, 0))
        sx, sy = getattr(self, 'exit_pos', (0, 0))
        P = self.PALETTE_MATRIX
        WALL = P["wall"]
        RESET = Style.RESET_ALL
        FORTY_TWO_WALL = P["forty_two"]
        ENTRY_ICON = "🚀 "
        EXIT_ICON = "🏁 "

        forty_two = self.forty_two_cells

        def is_42_cell(x: int, y: int) -> bool:
            return (x, y) in forty_two

        BOX = " ╴╷┐╶─┌┬╵┘│┤└┴├┼"

        def h_seg(x: int, iy: int) -> bool:
            if iy < h and grid[iy][x] & 1:
                return True
            if iy > 0 and grid[iy - 1][x] & 4:
                return True
            return False

        def v_seg(ix: int, y: int) -> bool:
            if ix < w and grid[y][ix] & 8:
                return True
            if ix > 0 and grid[y][ix - 1] & 2:
                return True
            return False

        def h_wall_color(x: int, iy: int) -> str:
            blue = False
            if iy < h and (grid[iy][x] & 1) and is_42_cell(x, iy):
                blue = True
            if iy > 0 and (grid[iy - 1][x] & 4) and is_42_cell(x, iy - 1):
                blue = True
            return FORTY_TWO_WALL if blue else WALL

        def v_wall_color(ix: int, y: int) -> str:
            blue = False
            if ix < w and (grid[y][ix] & 8) and is_42_cell(ix, y):
                blue = True
            if ix > 0 and (grid[y][ix - 1] & 2) and is_42_cell(ix - 1, y):
                blue = True
            return FORTY_TWO_WALL if blue else WALL

        def junction_color(ix: int, iy: int, up: bool,
                           down: bool, left: bool, right: bool) -> str:
            blue = False
            if left and ix > 0 and iy <= h:
                blue = blue or (h_wall_color(ix - 1, iy) == FORTY_TWO_WALL)
            if right and ix < w and iy <= h:
                blue = blue or (h_wall_color(ix, iy) == FORTY_TWO_WALL)
            if up and iy > 0 and ix <= w:
                if (iy - 1) < h:
                    blue = blue or (v_wall_color(ix, iy - 1) == FORTY_TWO_WALL)
            if down and iy < h and ix <= w:
                blue = blue or (v_wall_color(ix, iy) == FORTY_TWO_WALL)
            return FORTY_TWO_WALL if blue else WALL

        for iy in range(h + 1):
            top = ""
            for ix in range(w + 1):
                up = iy > 0 and v_seg(ix, iy - 1)
                down = iy < h and v_seg(ix, iy)
                left = ix > 0 and h_seg(ix - 1, iy)
                right = ix < w and h_seg(ix, iy)
                box_idx = (
                    int(left)
                    + int(down) * 2
                    + int(right) * 4
                    + int(up) * 8
                )
                top += (
                    junction_color(ix, iy, up, down, left, right)
                    + BOX[box_idx]
                    + RESET
                )
                if ix < w:
                    top += (
                        (h_wall_color(ix, iy) + "───" + RESET)
                        if h_seg(ix, iy)
                        else "   "
                    )
            print(top)

            if iy < h:
                mid = ""
                for ix in range(w + 1):
                    mid += (
                        (v_wall_color(ix, iy) + "│" + RESET)
                        if v_seg(ix, iy)
                        else " "
                    )
                    if ix < w:
                        if (ix, iy) == (ex, ey):
                            mid += P["entry"] + ENTRY_ICON + RESET
                        elif (ix, iy) == (sx, sy):
                            mid += P["exit"] + EXIT_ICON + RESET
                        elif (ix, iy) in self.path_connections:
                            dirs = self.path_connections[(ix, iy)]
                            # Reuse the BOX table: W=1, S=2, E=4, N=8
                            idx = (
                                (1 if 'W' in dirs else 0)
                                + (2 if 'S' in dirs else 0)
                                + (4 if 'E' in dirs else 0)
                                + (8 if 'N' in dirs else 0)
                            )
                            BOX_PATH = " ╴╷┐╶─┌┬╵┘│┤└┴├┼"
                            ch = BOX_PATH[idx]
                            left = "─" if 'W' in dirs else " "
                            right = "─" if 'E' in dirs else " "
                            mid += P["path"] + left + ch + right + RESET
                        else:
                            mid += "   "
                print(mid)
