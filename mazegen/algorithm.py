from abc import ABC, abstractmethod
from typing import Any, ClassVar

from model.maze import Maze


class Algorithm(ABC):

    perfect: ClassVar[bool]  # True = perfect maze, False = imperfect

    # Pixelated "42" shape — 15 means the cell must be
    # fully isolated (value 15), 0 means it can be carved through.
    # Dimensions: 5 rows × 7 cols
    # ("4" = cols 0-2, gap col 3, "2" = cols 4-6)
    PATTERN_42: list[list[int]] = [
        [15, 0, 15, 0, 15, 15, 15],
        [15, 0, 15, 0, 0, 0, 15],
        [15, 15, 15, 0, 15, 15, 15],
        [0, 0, 15, 0, 15, 0, 0],
        [0, 0, 15, 0, 15, 15, 15],
    ]

    def __init__(self, maze: Maze) -> None:
        self.maze = maze
        self.width = maze.width
        self.height = maze.height
        self.forty_two_cells: set[tuple[int, int]] = set()
        self.track: list[Any] = []

        self.directions = {
                'N': (0, -1),
                'E': (1, 0),
                'S': (0, 1),
                'W': (-1, 0),
            }

    @abstractmethod
    def generate(self) -> list[Any]:
        pass

    def place_42_center(self) -> set[tuple[int, int]]:
        """Place le motif '42' au centre du labyrinthe.

        Retourne le set des cellules occupées par le motif.
        Retourne un set vide si la taille du labyrinthe est insuffisante
        (le motif requiert au minimum pw+4 colonnes et ph+4 lignes pour
        laisser une marge de 2 cellules de chaque côté).
        """
        maze = self.maze
        ph = len(self.PATTERN_42)
        pw = len(self.PATTERN_42[0])

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
                if self.PATTERN_42[dy][dx] == 15:
                    x = start_x + dx
                    y = start_y + dy
                    maze.grid[y][x] = 15
                    self.forty_two_cells.add((x, y))

        return self.forty_two_cells

    def _get_42_neighbors(self) -> list[tuple[int, int]]:
        """Retourne les cellules voisines du motif '42' (hors motif)."""
        pattern_neighbors: list[tuple[int, int]] = []
        for cell in self.forty_two_cells:
            for neighbor in self._get_neighbors_of_cell(*cell):
                if (neighbor[0], neighbor[1]) not in self.forty_two_cells and (
                    neighbor[0],
                    neighbor[1],
                ) not in pattern_neighbors:
                    pattern_neighbors.append((neighbor[0], neighbor[1]))
        return pattern_neighbors

    def _get_neighbors_of_cell(
        self, x: int, y: int
    ) -> list[tuple[int, int, str]]:
        neighbors = []
        for direction, (offset_x, offset_y) in self.directions.items():
            nx = x + offset_x
            ny = y + offset_y
            if 0 <= nx < self.width and 0 <= ny < self.height:
                neighbors.append((nx, ny, direction))
        return neighbors

    def _get_direction_neighbor(
        self, x: int, y: int, dir: str
    ) -> tuple[int, int]:
        nx, ny = self.directions[dir]
        return (x + nx, y + ny)

    def _get_maze_boundaries(self) -> set[tuple[int, int]]:
        # Check top and bottom rows:
        boundaries: set[tuple[int, int]] = set()
        for x in range(self.width):
            boundaries.add((x, 0))
            boundaries.add((x, self.height - 1))
        # Check left and right columns:
        for y in range(self.height):
            boundaries.add((0, y))
            boundaries.add((self.width - 1, y))
        return boundaries
