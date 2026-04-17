from .algorithm import Algorithm
import random


class Backtracker(Algorithm):
    perfect: bool = True

    def _get_neighbors_of_cell(self, x: int,
                               y: int) -> list[tuple[int, int, str]]:
        """Returns a list of valid neighboring cells in
            the format (nx, ny, direction)."""

        neighbors = []

        for direction, (offset_x, offset_y) in self.maze._DIRECTIONS.items():

            nx = x + offset_x
            ny = y + offset_y

            if 0 <= nx < self.width and 0 <= ny < self.height:

                neighbors.append((nx, ny, direction))

        return neighbors

    def generate(self) -> list[str]:
        """Generates the maze using a depth-first search
            (backtracking) algorithm."""

        start: tuple[int, int] = (0, 0)
        visited: set[tuple[int, int]] = set(self.forty_two_cells)
        stack: list[tuple[int, int]] = []

        visited.add(start)
        stack.append(start)

        while stack:

            current_cell: tuple[int, int] = stack[-1]
            x, y = current_cell

            neighbors: list[tuple[int, int, str]] = [
                (nx, ny, direction)
                for nx, ny, direction in self._get_neighbors_of_cell(x, y)
                if (nx, ny) not in visited
            ]

            if not neighbors:
                stack.pop()
                self.tracks.append((x, y, "backtrack"))
                continue

            else:

                nx, ny, direction = random.choice(neighbors)
                self.maze.remove_wall(x, y, direction)
                visited.add((nx, ny))
                stack.append((nx, ny))
                self.tracks.append((x, y, direction))

        return self.tracks
