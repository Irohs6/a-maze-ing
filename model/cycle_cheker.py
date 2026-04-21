from model.maze import Maze


class Cycle_Checker:
    def __init__(self, maze: Maze) -> None:
        self.maze = maze

    def has_cycle(self) -> bool:
       
        widht = self.maze.width
        height = self.maze.height

        nodes = widht * height
        edges = 0

        for y in range(height):
            for x in range(widht):
                if x < widht - 1 and not self.maze.has_wall(x, y, 'E'):
                    edges += 1
                if y < height - 1 and not self.maze.has_wall(x, y, 'S'):
                    edges += 1
        return edges >= nodes
