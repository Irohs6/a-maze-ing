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
            {(x, y)}
            for x in range(self.width)
            for y in range(self.height)
            if (x, y) not in self.forty_two_cells
        ]
        self._union[0] = self.forty_two_cells.union(self._union[0])

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

    def _is_42_wall(self, x: int, y: int, wall_direction: str) -> bool:
        if (
            self._get_direction_neighbor(x, y, wall_direction)
            not in self.forty_two_cells and (x, y) not in self.forty_two_cells
        ):
            return False
        else:
            return True

    def _get_breakable_walls(self) -> list[str]:
        eligible_walls: list[str] = []
        for y in range(self.height):
            for x in range(self.width):
                for direction in ["N", "E", "S", "W"]:
                    if (
                        self.maze.has_wall(x, y, direction)
                        and self._get_direction_neighbor(x, y, direction)
                        not in self.forty_two_cells
                        and not self.maze._is_border_wall(x, y, direction)
                        and not self._is_42_wall(x, y, direction)
                        and self._cell_wall_count(x, y) > 2
                    ):
                        eligible_walls.append((x, y, direction))
        return eligible_walls

    def _no_open_area_around(self, original_x: int, original_y: int) -> bool:
        """Return True if the 3×3 block whose top-left is (start_x, start_y)
        has no inner walls."""
        maze = self.maze
        # Horizontal passages (East direction) between adjacent columns
        # representation visuel de la zone 3x3 interdite :
        #   x0,y0 E x1,y0 E x2,y0
        #     0   |   1   |   2
        #   x0,y1 | x1,y1 | x2,y1
        #   x0,y2 | x1,y2 | x2,y2
        start_y = 0 if original_y - 4 <= 0 else original_y - 4
        start_x = 0 if original_x - 4 <= 0 else original_x - 4
        for y in range(start_y - 4, start_y + 4):
            for x in range(start_x - 3, start_x + 3):
                if maze.has_wall(x, y, "E"):
                    return False
        # Vertical passages (South direction) between adjacent rows
        for y in range(start_y - 3, start_y + 3):
            for x in range(start_x - 4, start_x + 4):
                if maze.has_wall(x, y, "S"):
                    return False
        return True

    def second_loop(self) -> None:
        """For imperfect mazes, break an additional 15% of the walls
            that are not part of the 42 shape or borders."""

        _eligible_walls = self._get_breakable_walls()
        len_to_break = int(len(_eligible_walls) * 0.15)
        random.shuffle(_eligible_walls)
        while len_to_break > 0:
            if not _eligible_walls:
                break
            x, y, wall_direction = _eligible_walls.pop()
            len_to_break -= 1
            self.maze.remove_wall(x, y, wall_direction)
            if self._no_open_area_around(x, y):
                self.maze.add_wall(x, y, wall_direction)
                # Revert if it creates a forbidden open area
            else:
                self.tracks.append((x, y, wall_direction))
