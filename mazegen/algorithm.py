from abc import ABC, abstractmethod
from model.maze import Maze


class Algorithm(ABC):
    def __init__(self, maze: Maze) -> None:
        self.maze = maze
        self.width = maze.width
        self.height = maze.height
        self.forty_two_cells: set = set()
        self.track: list = []

    @abstractmethod
    def generate(self) -> list:
        pass

    def place_42_center(self) -> set:
        """Place le motif '42' au centre du labyrinthe.

        Retourne le set des cellules occupées par le motif.
        Retourne un set vide si la taille du labyrinthe est insuffisante
        (le motif requiert au minimum pw+4 colonnes et ph+4 lignes pour
        laisser une marge de 2 cellules de chaque côté).
        """
        maze = self.maze
        ph = len(maze.PATTERN_42)
        pw = len(maze.PATTERN_42[0])

        # Marge minimale de 2 cellules de chaque côté
        if maze.width < pw + 4 or maze.height < ph + 4:
            print(
                f"[INFO] Labyrinthe trop petit ({maze.width}x{maze.height}) "
                f"pour le motif '42' (min {pw + 4}x{ph + 4}) — motif omis."
            )
            return set()

        start_x = (maze.width - pw) // 2
        start_y = (maze.height - ph) // 2

        for dy in range(ph):
            for dx in range(pw):
                if maze.PATTERN_42[dy][dx] == 15:
                    x = start_x + dx
                    y = start_y + dy
                    maze.grid[y][x] = 15
                    self.forty_two_cells.add((x, y))

        return self.forty_two_cells

    def _get_42_neighbors(self) -> list:
        """Retourne les cellules voisines du motif '42' (hors motif)."""
        pattern_neighbors = []
        for cell in self.forty_two_cells:
            for neighbor in self.maze._get_neighbors_of_cell(*cell):
                if (neighbor[0], neighbor[1]) not in self.forty_two_cells and (
                    neighbor[0],
                    neighbor[1],
                ) not in pattern_neighbors:
                    pattern_neighbors.append((neighbor[0], neighbor[1]))
        return pattern_neighbors
