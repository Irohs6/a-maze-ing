import copy
import random

from .algorithm import Algorithm
from model.maze import Maze
from model.maze_validator import MazeValidator


class Kruksal(Algorithm):
    perfect: bool = False

    # Maximum number of global attempts before giving up
    _MAX_GLOBAL_ATTEMPTS: int = 30

    def _breakable_walls(self, maze, x, y, pattern_cells):
        eligible_walls = []
        for direction in ['N', 'E', 'S', 'W']:
            if (maze.has_wall(x, y, direction)
                    and self._get_direction_neighbor(x, y, direction)
                    not in pattern_cells
                    and not maze._is_border_wall(x, y, direction)
                    and not self._is_42_wall(x, y, direction)):
                eligible_walls.append(direction)
        return eligible_walls

    def _second_loop(self, maze: Maze, wall_count, pattern_cells,
                     tracks) -> Maze:
        _to_destroy: set[tuple[int, int]] = [
            (x, y)
            for x in range(self.width)
            for y in range(self.height)
            if self._cell_wall_count(maze, x, y) > 2
            and (x, y) not in pattern_cells and (x, y) not in self._boundaries
        ]
        random.shuffle(_to_destroy)
        for x, y in _to_destroy:
            while wall_count[(x, y)] > 2:
                eligible_walls = self._breakable_walls(maze, x,
                                                       y, pattern_cells)

                if not eligible_walls:
                    break

                wall_direction = random.choice(eligible_walls)
                maze.remove_wall(x, y, wall_direction)
                tracks.append((x, y, wall_direction))
                wall_count[(x, y)] -= 1

        return (maze, tracks)

    def _is_42_wall(self, x, y, wall_direction) -> bool:
        if self._get_direction_neighbor(x, y, wall_direction
                                        ) not in self.forty_two_cells:
            return False
        else:
            return True

    @staticmethod
    def _cell_wall_count(maze: Maze, x: int, y: int) -> int:
        """Return the number of walls surrounding cell (x, y) (0–4)."""
        return maze.grid[y][x].bit_count()

    def generate(self) -> list[tuple[int, int, str]]:
        """Generates the maze using a randomized version
        of Kruskal's algorithm."""

        self.forty_two_cells = self.maze.forty_two_cells
        for _attempt in range(self._MAX_GLOBAL_ATTEMPTS):
            # Reset the maze and related attributes for a fresh attempt
            maze_attempt = copy.copy(self.maze)
            maze_attempt.grid = [row[:] for row in self.maze.grid]
            self.track = []

            tracks = []
            pattern_cells = maze_attempt.forty_two_cells

            unvisited = [
                (x, y)
                for x in range(self.width)
                for y in range(self.height)
                if (x, y) not in pattern_cells
            ]
            if not unvisited:
                continue
            random.shuffle(unvisited)
            for x, y in unvisited:
                eligible_walls = self._breakable_walls(maze_attempt, x, y,
                                                       pattern_cells)

                if not eligible_walls:
                    continue

                else:
                    wall_direction = random.choice(eligible_walls)
                    maze_attempt.remove_wall(x, y, wall_direction)
                    tracks.append((x, y, wall_direction))

            wall_count_base: dict[tuple[int, int], int] = {
                (x, y): c
                for x in range(self.width)
                for y in range(self.height)
                if (x, y) not in self._boundaries
                and (c := self._cell_wall_count(maze_attempt, x, y)) > 2
            }

            potential_maze = copy.copy(maze_attempt)
            potential_maze.grid = [row[:] for row in maze_attempt.grid]
            validator = MazeValidator(potential_maze)
            counter = 0
            until_now = len(tracks)
            while (
                not validator._validate_maze_connectivity() or
                validator._has_forbidden_open_areas()
            ):
                tracks = tracks[:until_now]
                for y_idx in range(self.height):
                    potential_maze.grid[y_idx][:] = maze_attempt.grid[y_idx]
                wall_count = wall_count_base.copy()
                potential_maze, tracks = self._second_loop(potential_maze,
                                                           wall_count,
                                                           pattern_cells,
                                                           tracks)
                counter += 1

                if counter >= 50:
                    # Abandon this attempt, start over
                    break

            else:
                # The while loop ended without a break → valid maze found
                for i in range(len(self.maze.grid)):
                    for j in range(len(self.maze.grid[i])):
                        self.maze.grid[i][j] = potential_maze.grid[i][j]
                self.forty_two_cells = self.maze.forty_two_cells
                self.track = tracks
                return tracks

        raise ValueError(
            f"Kruskal: impossible to generate a valid maze "
            f"in {self._MAX_GLOBAL_ATTEMPTS} "
            f"attempts ({self.width}x{self.height})"
        )
