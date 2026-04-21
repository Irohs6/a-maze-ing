from model.maze import Maze


class Cycle_Checker:
    def __init__(self, maze: Maze) -> None:
        self.maze = maze
        self.visited = set()
        self.counter = 0

    def has_cycle(self) -> bool:
        """
        Returns True if the maze contains at least one cycle (i.e., is imperfect).
        Utilise un DFS itératif pour éviter la récursion infinie et vérifie les murs dans les deux sens.
        """
        self.visited = set()
        directions = {
            "N": (0, -1, "S"),
            "E": (1, 0, "W"),
            "S": (0, 1, "N"),
            "W": (-1, 0, "E"),
        }

        for y in range(self.maze.height):
            for x in range(self.maze.width):
                if (x, y) in self.visited:
                    continue
                stack = [((x, y), None)]  # (cell, parent)
                while stack:
                    (cx, cy), parent = stack.pop()
                    if (cx, cy) in self.visited:
                        continue
                    self.visited.add((cx, cy))
                    for dir, (dx, dy, opp_dir) in directions.items():
                        nx, ny = cx + dx, cy + dy
                        if (
                            0 <= nx < self.maze.width
                            and 0 <= ny < self.maze.height
                        ):
                            # Passage ouvert dans les deux sens
                            if not self.maze.has_wall(
                                cx, cy, dir
                            ) and not self.maze.has_wall(nx, ny, opp_dir):
                                if (nx, ny) not in self.visited:
                                    stack.append(((nx, ny), (cx, cy)))
                                elif (nx, ny) != parent:
                                    return True
        return False
