from abc import ABC, abstractmethod
from typing import Any
from model.maze import Maze
from model.maze_validator import MazeValidator
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

    def _cell_wall_count(self, x: int, y: int) -> int:
        """Return the number of walls surrounding cell (x, y) (0–4)."""
        return self.maze.grid[y][x].bit_count()

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
        """Returns True if there is no fully open 3x3 block (without internal
        walls) in the 9x9 area centered on (original_x, original_y).
        Returns False if at least one forbidden 3x3 open block is found.
        Uses MazeValidator._is_3x3_open for detection.
        """

        validator = MazeValidator(self.maze)

        # Check all 3x3 blocks in the 9x9 area around the original cell
        for dy in range(-2, 1):
            for dx in range(-2, 1):
                top_left_x = original_x + dx
                top_left_y = original_y + dy
                if 0 <= top_left_x <= self.width - 3 and \
                   0 <= top_left_y <= self.height - 3:
                    if validator._is_3x3_open(top_left_x, top_left_y):
                        return False
        return True

    def second_loop(self) -> None:
        """For imperfect mazes, break an additional 30% of the walls
            that are not part of the 42 shape or borders.
            Log the number of walls actually opened."""

        _eligible_walls = self._get_breakable_walls()
        len_to_break = int(len(_eligible_walls) * 0.3)
        random.shuffle(_eligible_walls)
        while len_to_break > 0:
            if not _eligible_walls:
                break
            x, y, wall_direction = _eligible_walls.pop()
            len_to_break -= 1

            self.maze.remove_wall(x, y, wall_direction)
            if not self._no_open_area_around(x, y):
                # Removing this wall created a forbidden 3x3 
                # open area: restore it
                self.maze.add_wall(x, y, wall_direction)

            else:
                self.tracks.append((x, y, wall_direction))
