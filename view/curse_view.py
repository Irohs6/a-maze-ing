import curses
from model.maze import Maze

BOX = " ╴╷┐╶─┌┬╵┘│┤└┴├┼"


class CursesView:
    def __init__(self, maze, track=None, entry=(0,0), exit=(0,0)):
        self.maze = maze
        self.track = track
        self.entry = entry
        self.exit = exit
        self._anim_maze = Maze(maze.width, maze.height)

    # ---------------------------------------------------------
    #  LANCEMENT CURSES
    # ---------------------------------------------------------
    def start(self):
        curses.wrapper(self._main)

    def _main(self, stdscr):
        self.stdscr = stdscr
        curses.curs_set(0)
        stdscr.clear()

        self._draw_maze(self.maze)

        if self.track:
            # Détecte le format du track (backtracker: str, kruskal: tuple)
            if self.track and isinstance(self.track[0], tuple):
                self._play_animation_kruskal()
            else:
                self._play_animation()

        self._wait_for_exit()

    def _play_animation_kruskal(self, delay=0.03):
        import time
        anim = self._anim_maze
        for step in self.track:
            x, y, direction = step
            anim.remove_wall(x, y, direction)
            self._draw_maze(anim, cursor=(x, y))
            time.sleep(delay)

    # ---------------------------------------------------------
    #  DESSIN DU LABYRINTHE
    # ---------------------------------------------------------
    def _draw_maze(self, maze, cursor=None):
        h, w = maze.height, maze.width
        grid = maze.grid

        def h_seg(x, iy):
            if iy < h and grid[iy][x] & 1:
                return True
            if iy > 0 and grid[iy-1][x] & 4:
                return True
            return False

        def v_seg(ix, y):
            if ix < w and grid[y][ix] & 8:
                return True
            if ix > 0 and grid[y][ix-1] & 2:
                return True
            return False

        lines = []
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
            lines.append(top)

            if iy < h:
                mid = ""
                for ix in range(w + 1):
                    mid += "│" if v_seg(ix, iy) else " "
                    if ix < w:
                        if (ix, iy) == self.entry:
                            mid += " E "
                        elif (ix, iy) == self.exit:
                            mid += " S "
                        elif cursor == (ix, iy):
                            mid += " @ "
                        else:
                            mid += "   "
                lines.append(mid)

        # Affichage curses sécurisé
        max_y, max_x = self.stdscr.getmaxyx()
        too_wide = any(len(line) > max_x for line in lines)
        too_tall = len(lines) > max_y
        self.stdscr.clear()
        for y, line in enumerate(lines[:max_y]):
            self.stdscr.addstr(y, 0, line[:max_x])
        if too_wide or too_tall:
            warn = "[Labyrinthe trop grand pour la fenêtre]"
            self.stdscr.addstr(max(0, max_y-1), 0, warn[:max_x])
        self.stdscr.refresh()

    # ---------------------------------------------------------
    #  ANIMATION
    # ---------------------------------------------------------
    def _play_animation(self, delay=0.03):
        import time

        directions = {
            'N': (0, -1),
            'E': (1, 0),
            'S': (0, 1),
            'W': (-1, 0),
        }

        pos_stack = [(0, 0)]
        anim = self._anim_maze

        for step in self.track:
            if step != "BACK":
                x, y = pos_stack[-1]
                dx, dy = directions[step]
                nx, ny = x + dx, y + dy
                anim.remove_wall(x, y, step)
                pos_stack.append((nx, ny))
            else:
                if len(pos_stack) > 1:
                    pos_stack.pop()

            self._draw_maze(anim, cursor=pos_stack[-1])
            time.sleep(delay)

    # ---------------------------------------------------------
    #  ATTENTE FIN
    # ---------------------------------------------------------
    def _wait_for_exit(self):
        while True:
            key = self.stdscr.getch()
            if key in (ord('q'), ord('Q')):
                break
