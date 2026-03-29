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

from collections import deque


class TerminalView:
    """Renders the maze as ASCII art in the terminal.

    Reads a Maze object and constructs an ASCII representation using characters
    for walls (e.g., +, -, |) and spaces for passages. Handles display of:
        - entrance and exit with distinct markers
        - solution path (shown or hidden on demand)
        - wall colors via ANSI codes
        - "42" pattern with optional different color

    Implements user interactions in terminal mode:
        'r' to regenerate, 's' to toggle solution display, 'c' to change colors.
    """

    def __init__(self, maze):
        self.maze = maze

    def print_unicode(self) -> None:
        """Print the maze using Unicode box-drawing characters."""
        maze = self.maze
        h = maze.height
        w = maze.width
        grid = maze.grid

        # Index: left + down*2 + right*4 + up*8
        BOX = " ╴╷┐╶─┌┬╵┘│┤└┴├┼"

        def h_seg(x, iy):
            """Is there a horizontal wall above row iy at column x?"""
            if iy < h and grid[iy][x] & 1:
                return True
            if iy > 0 and grid[iy - 1][x] & 4:
                return True
            return False

        def v_seg(ix, y):
            """Is there a vertical wall left of column ix at row y?"""
            if ix < w and grid[y][ix] & 8:
                return True
            if ix > 0 and grid[y][ix - 1] & 2:
                return True
            return False

        for iy in range(h + 1):
            # Intersection + horizontal walls line
            top = ""
            for ix in range(w + 1):
                up = iy > 0 and v_seg(ix, iy - 1)
                down = iy < h and v_seg(ix, iy)
                left = ix > 0 and h_seg(ix - 1, iy)
                right = ix < w and h_seg(ix, iy)
                top += BOX[int(left) + int(down) * 2 + int(right) * 4 + int(up) * 8]
                if ix < w:
                    top += "───" if h_seg(ix, iy) else "   "
            print(top)

            # Cell content + vertical walls line
            if iy < h:
                mid = ""
                for ix in range(w + 1):
                    mid += "│" if v_seg(ix, iy) else " "
                    if ix < w:
                        mid += "   "
                print(mid)

    def print_connectivity_debug(self) -> None:
        """Appelle _validate_maze_connectivity() et affiche le résultat visuellement.

        Appelle la fonction du validator pour obtenir le résultat (True/False),
        puis colorie chaque cellule pour montrer ce que la fonction a analysé.

        Colors:
            green (·): cell reachable from (0, 0).
            blue  (■): isolated cell (value == 15, part of the "42" pattern).
            red   (✗): unreachable cell — la fonction retournera False.
        """
        from model.maze_validator import MazeValidator

        maze = self.maze
        h = maze.height
        w = maze.width
        grid = maze.grid

        validator = MazeValidator(maze)
        result = validator._validate_maze_connectivity()

        # BFS identique à celui dans _validate_maze_connectivity, pour colorer les cellules
        directions = {'N': (0, -1), 'E': (1, 0), 'S': (0, 1), 'W': (-1, 0)}
        queue = deque([(0, 0)])
        visited = set()
        while queue:
            x, y = queue.popleft()
            if grid[y][x] == 15 or (x, y) in visited:
                continue
            visited.add((x, y))
            for direction, (dx, dy) in directions.items():
                if not maze.has_wall(x, y, direction):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in visited:
                        queue.append((nx, ny))

        GREEN = "\033[32m"
        RED   = "\033[31m"
        BLUE  = "\033[34m"
        RESET = "\033[0m"

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
                up    = iy > 0 and v_seg(ix, iy - 1)
                down  = iy < h and v_seg(ix, iy)
                left  = ix > 0 and h_seg(ix - 1, iy)
                right = ix < w and h_seg(ix, iy)
                top += BOX[int(left) + int(down) * 2 + int(right) * 4 + int(up) * 8]
                if ix < w:
                    top += "───" if h_seg(ix, iy) else "   "
            print(top)

            if iy < h:
                mid = ""
                for ix in range(w + 1):
                    mid += "│" if v_seg(ix, iy) else " "
                    if ix < w:
                        if grid[iy][ix] == 15:
                            mid += f"{BLUE} ■ {RESET}"
                        elif (ix, iy) in visited:
                            mid += f"{GREEN} · {RESET}"
                        else:
                            mid += f"{RED} ✗ {RESET}"
                print(mid)

        print(f"\n{GREEN} · {RESET} reachable   "
              f"{BLUE} ■ {RESET} isolated (42)   "
              f"{RED} ✗ {RESET} unreachable")

        if result:
            print(f"\n_validate_maze_connectivity() → {GREEN}True ✓{RESET}  (labyrinthe connexe)")
        else:
            print(f"\n_validate_maze_connectivity() → {RED}False ✗{RESET}  (cellules inaccessibles détectées)")


if __name__ == "__main__":
    from model.maze import Maze

    maze = Maze(5, 5)
    view = TerminalView(maze)
    view.print_unicode()

    # Petit labyrinthe 4x3 câblé manuellement pour tester le visualiseur.
    # Chaque cellule : bits N=1, E=2, S=4, W=8  (15 = murs sur les 4 côtés)
    maze = Maze(4, 3)
    # Ligne 0
    maze.grid[0][0] = 0b1001  # N+W fermés (coin haut-gauche)
    maze.grid[0][1] = 0b0001  # N fermé
    maze.grid[0][2] = 0b0001  # N fermé
    maze.grid[0][3] = 0b0011  # N+E fermés (coin haut-droit)
    # Ligne 1
    maze.grid[1][0] = 0b1111  # W fermé
    maze.grid[1][1] = 0b1111 # ouvert
    maze.grid[1][2] = 0b1111  # ouvert
    maze.grid[1][3] = 0b1111  # E fermé
    # Ligne 2
    maze.grid[2][0] = 0b1111  # S+W fermés (coin bas-gauche)
    maze.grid[2][1] = 0b0100  # S fermé
    maze.grid[2][2] = 0b0100  # S fermé
    maze.grid[2][3] = 0b0110  # S+E fermés (coin bas-droit)

    view = TerminalView(maze)
    view.print_connectivity_debug()

