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
