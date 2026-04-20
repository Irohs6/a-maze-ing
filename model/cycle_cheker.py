from model.maze import Maze


class Cycle_Checker:
    def __init__(self, maze: Maze) -> None:
        self.maze = maze
        self.visited = set()
        self.counter = 0

    def has_cycle(self) -> bool:
        """Check if the maze contains a cycle by counting
            the number of open paths.
        A perfect maze should have exactly width*height - 1 open paths."""

        for y in range(self.maze.height):
            for x in range(self.maze.width):
                for direction in ["N", "E", "S", "W"]:
                    if not self.maze.has_wall(x, y, direction):
                        self.counter += 1

        return self.counter >= self.maze.width * self.maze.height - 1
