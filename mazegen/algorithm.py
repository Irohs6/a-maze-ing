from abc import ABC, abstractmethod
from typing import Any, ClassVar

from model.maze import Maze


class Algorithm(ABC):

    perfect: ClassVar[bool]  # True = perfect maze, False = imperfect

    # Pixelated "42" shape — 15 means the cell must be
    # fully isolated (value 15), 0 means it can be carved through.
    # Dimensions: 5 rows × 7 cols
    # ("4" = cols 0-2, gap col 3, "2" = cols 4-6)

    def __init__(self, maze: Maze) -> None:
        self.maze = maze
        self.width = maze.width
        self.height = maze.height
        self.forty_two_cells: set[tuple[int, int]] = set()
        self.track: list[Any] = []
        self._boundaries: set[tuple[int, int]] = self._get_maze_boundaries()

    @abstractmethod
    def generate(self) -> list[Any]:
        pass

    def _get_neighbors_of_cell(
        self, x: int, y: int
    ) -> list[tuple[int, int, str]]:
        neighbors = []
        for direction, (offset_x, offset_y) in self.maze._DIRECTIONS.items():
            nx = x + offset_x
            ny = y + offset_y
            if 0 <= nx < self.width and 0 <= ny < self.height:
                neighbors.append((nx, ny, direction))
        return neighbors

    def _get_direction_neighbor(
        self, x: int, y: int, direction: str
    ) -> tuple[int, int]:
        nx, ny = self.maze._DIRECTIONS[direction]
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
