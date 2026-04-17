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
        self.forty_two_cells = maze.forty_two_cells
        self.tracks: list[Any] = []
        self._boundaries: set[tuple[int, int]] = self._get_maze_boundaries()
        self._union = [
            self.forty_two_cells.union({(0, 0)})
        ]
        self._union.extend([
            {(x, y)}
            for x in range(self.width)
            for y in range(self.height)
            if (x, y) not in self.forty_two_cells
        ])

    @abstractmethod
    def generate(self) -> list[Any]:
        pass

    def _get_direction_neighbor(
        self, x: int, y: int, direction: str
    ) -> tuple[int, int]:
        """Return the coordinates of the neighboring 
            cell in the given direction."""

        nx, ny = self.maze._DIRECTIONS[direction]
        return (x + nx, y + ny)

    def _get_maze_boundaries(self) -> set[tuple[int, int]]:
        """Return a set of coordinates representing the maze boundaries."""

        boundaries: set[tuple[int, int]] = set()

        for x in range(self.width):
            boundaries.add((x, 0))
            boundaries.add((x, self.height - 1))

        for y in range(self.height):
            boundaries.add((0, y))
            boundaries.add((self.width - 1, y))
        return boundaries

