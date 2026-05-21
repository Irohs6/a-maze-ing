from .maze import Maze


class CycleChecker:
    """Detects cycles in a maze using an edge/node count heuristic."""

    def __init__(self, maze: Maze) -> None:
        """Initialize the checker with a generated maze."""
        self.maze = maze

    def has_cycle(self) -> bool:
        """Return True if the maze contains at least one cycle."""

        width = self.maze.width
        height = self.maze.height

        nodes = width * height - len(self.maze.forty_two_cells)
        edges = 0

        for y in range(height):
            for x in range(width):
                if (x, y) in self.maze.forty_two_cells:
                    continue
                else:
                    if x < width - 1 and not self.maze.has_wall(x, y, 'E'):
                        edges += 1
                    if y < height - 1 and not self.maze.has_wall(x, y, 'S'):
                        edges += 1
        return edges >= nodes
