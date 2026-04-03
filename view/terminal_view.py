# view/terminal_view.py

import os
import time
from collections import deque
from model.maze import Maze


class TerminalView:
    def __init__(self, maze, track=None, entry=(0, 0), exit=(0, 0)):
        self.maze = maze
        self.track = track
        self.entry = entry
        self.exit_pos = exit
        # Maze vierge dédié à l'animation — les murs sont cassés au fur et
        # à mesure du track pour que la progression reste 100 % visible.
        self._anim_maze = Maze(maze.width, maze.height)

    # ---------------------------------------------------------
    #  ANIMATION DE LA GÉNÉRATION
    # ---------------------------------------------------------
    def play(self, delay=0.03):
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

    def play_kruksal(self, delay=0.03):
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
    def _print_with_cursor(self, cursor_pos, maze=None):
        if maze is None:
            maze = self.maze
        h = maze.height
        w = maze.width
        grid = maze.grid

        cx, cy = cursor_pos
        ex, ey = self.entry
        sx, sy = self.exit_pos

        BOX = " ╴╷┐╶─┌┬╵┘│┤└┴├┼"

        def h_seg(x, iy):
            if iy < h and grid[iy][x] & 1:
                return True
            if iy > 0 and grid[iy - 1][x] & 4:
                return True
            return False

        def v_seg(ix, y):
            if ix < w and grid[y][ix] & 8:
                return True
            if ix > 0 and grid[y][ix - 1] & 2:
                return True
            return False

        GREEN = "\033[32m"
        RESET = "\033[0m"
        ENTRY_ICON = " E "  # Largeur fixe
        EXIT_ICON = " S "   # Largeur fixe

        for iy in range(h + 1):
            top = ""
            for ix in range(w + 1):
                up = iy > 0 and v_seg(ix, iy - 1)
                down = iy < h and v_seg(ix, iy)
                left = ix > 0 and h_seg(ix - 1, iy)
                right = ix < w and h_seg(ix, iy)
                top += BOX[int(left) + int(down)*2 + int(right)*4 + int(up)*8]
                if ix < w:
                    top += "───" if h_seg(ix, iy) else "   "
            print(top)

            if iy < h:
                mid = ""
                for ix in range(w + 1):
                    mid += "│" if v_seg(ix, iy) else " "
                    if ix < w:
                        if (ix, iy) == (cx, cy):
                            mid += f"{GREEN} ● {RESET}"
                        elif (ix, iy) == (ex, ey):
                            mid += ENTRY_ICON
                        elif (ix, iy) == (sx, sy):
                            mid += EXIT_ICON
                        else:
                            mid += "   "
                print(mid)

    # ---------------------------------------------------------
    #  AFFICHAGE FINAL
    # ---------------------------------------------------------
    def print_unicode(self):
        maze = self.maze
        h = maze.height
        w = maze.width
        grid = maze.grid

        ex, ey = getattr(self, 'entry', (0, 0))
        sx, sy = getattr(self, 'exit_pos', (0, 0))
        ENTRY_ICON = " E "
        EXIT_ICON = " S "

        BOX = " ╴╷┐╶─┌┬╵┘│┤└┴├┼"

        def h_seg(x, iy):
            if iy < h and grid[iy][x] & 1:
                return True
            if iy > 0 and grid[iy - 1][x] & 4:
                return True
            return False

        def v_seg(ix, y):
            if ix < w and grid[y][ix] & 8:
                return True
            if ix > 0 and grid[y][ix - 1] & 2:
                return True
            return False

        for iy in range(h + 1):
            top = ""
            for ix in range(w + 1):
                up = iy > 0 and v_seg(ix, iy - 1)
                down = iy < h and v_seg(ix, iy)
                left = ix > 0 and h_seg(ix - 1, iy)
                right = ix < w and h_seg(ix, iy)
                top += BOX[int(left) + int(down)*2 + int(right)*4 + int(up)*8]
                if ix < w:
                    top += "───" if h_seg(ix, iy) else "   "
            print(top)

            if iy < h:
                mid = ""
                for ix in range(w + 1):
                    mid += "│" if v_seg(ix, iy) else " "
                    if ix < w:
                        if (ix, iy) == (ex, ey):
                            mid += ENTRY_ICON
                        elif (ix, iy) == (sx, sy):
                            mid += EXIT_ICON
                        else:
                            mid += "   "
                print(mid)
