from model.maze import Maze


class Cycle_Checker:
    def __init__(self, maze: Maze) -> None:
        self.maze = maze

    def has_cycle(self) -> bool:

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
