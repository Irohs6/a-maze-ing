from abc import ABC, abstractmethod
from typing import Any
from model.maze import Maze
from model import maze_validator
import random


class Algorithm(ABC):

    # Pixelated "42" shape — 15 means the cell must be
    # fully isolated (value 15), 0 means it can be carved through.
    # Dimensions: 5 rows × 7 cols
    # ("4" = cols 0-2, gap col 3, "2" = cols 4-6)

    def __init__(self, maze: Maze, is_perfect: bool) -> None:
        self.maze = maze
        self.width = maze.width
        self.height = maze.height
        self.forty_two_cells: set[tuple[int, int]] = set()
        self.forty_two_cells = maze.forty_two_cells
        self.is_perfect = is_perfect
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

    def _get_eligible_walls(self) -> list[tuple[int, int, str]]:
        self._eligible_walls = []
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
                        self._eligible_walls.append((x, y, direction))
        return self._eligible_walls

    def second_loop(self) -> None:
        """For imperfect mazes, break an additional 15% of the walls
            that are not part of the 42 shape or borders."""

        _eligible_walls = self._get_eligible_walls()
        len_to_break = int(len(_eligible_walls) * 0.15)
        random.shuffle(_eligible_walls)
        while len_to_break > 0:
            if not _eligible_walls:
                break
            x, y, wall_direction = _eligible_walls.pop()
            len_to_break -= 1
            self.maze.remove_wall(x, y, wall_direction)
            if maze_validator.MazeValidator(self.maze
                                            )._has_forbidden_open_areas():
                self.maze.add_wall(x, y, wall_direction)
                # Revert if it creates a forbidden open area
            self.tracks.append((x, y, wall_direction))
