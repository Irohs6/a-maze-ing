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
        self._eligible_walls = self._get_eligible_walls()

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

    def _is_42_wall(self, x, y, wall_direction) -> bool:
        if (
            self._get_direction_neighbor(x, y, wall_direction)
            not in self.forty_two_cells
        ):
            return False
        else:
            return True

    def _get_eligible_walls(self):
        walls = []
        directions = ["N", "E", "S", "W"]
        for y in range(self.height):
            for x in range(self.width):
                for direction in directions:
                    if (
                        self._get_direction_neighbor(x, y, direction)
                        not in self.forty_two_cells
                        and not self.maze._is_border_wall(x, y, direction)
                        and (x, y) not in self.forty_two_cells
                    ):
                        walls.append((x, y, direction))
        return walls
