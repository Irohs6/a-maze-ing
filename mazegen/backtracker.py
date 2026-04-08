from .algorithm import Algorithm
import random


class Backtracker(Algorithm):
    perfect: bool = True

    def generate(self) -> list[str]:
        """Generates the maze using a depth-first search
        (backtracking) algorithm."""
        start = (0, 0)
        visited = set(self.place_42_center())
        stack = []
        track = []

        visited.add(start)
        stack.append(start)

        while stack:
            current_cell = stack[-1]
            x, y = current_cell

            neighbors = [
                (nx, ny, direction)
                for nx, ny, direction in self._get_neighbors_of_cell(x, y)
                if (nx, ny) not in visited
            ]

            if not neighbors:
                stack.pop()
                continue
            else:
                nx, ny, direction = random.choice(neighbors)
                self.maze.remove_wall(x, y, direction)
                visited.add((nx, ny))
                stack.append((nx, ny))
                track.append((x, y, direction))

        self.track = track
        return track
