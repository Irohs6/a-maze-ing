import random
from .algorithm import Algorithm
from model.maze import Maze


class Kruksal(Algorithm):
    perfect: bool = False
    REVERSE: dict[str, str] = {'N': 'S', 'S': 'N', 'E': 'W', 'W': 'E'}
    # Maximum number of global attempts before giving up

    def _breakable_walls(self, x, y):
        eligible_walls = []
        for direction in ["N", "E", "S", "W"]:
            if (
                self.maze.has_wall(x, y, direction)
                and self._get_direction_neighbor(x, y, direction)
                not in self.forty_two_cells
                and not self.maze._is_border_wall(x, y, direction)
                and not self._is_42_wall(x, y, direction)
                and (x, y) not in self._union[0]
                and self._cell_wall_count(x, y) > 2
            ):
                eligible_walls.append(direction)
        return eligible_walls

    def _find_in_union(
        self, coordinates: tuple[int, int], neighbor: tuple[int, int]
    ) -> list[int] | bool:
        indexes = []
        for index, set in enumerate(self._union):
            if coordinates in set and neighbor in set:
                return False
            elif coordinates in set or neighbor in set:
                indexes.append(index)
        return indexes

    def _concatenate_in_union(self, indexes: list[int]):
        self._union[indexes[0]] = self._union[indexes[0]].union(self._union[indexes[1]])
        self._union.pop(indexes[1])

    def _second_loop(
        self, maze: Maze, wall_count, pattern_cells, tracks
    ) -> Maze:
        _to_destroy: set[tuple[int, int]] = [
            (x, y)
            for x in range(self.width)
            for y in range(self.height)
            if self._cell_wall_count(maze, x, y) > 2
            and (x, y) not in pattern_cells
            and (x, y) not in self._boundaries
        ]
        random.shuffle(_to_destroy)
        for x, y in _to_destroy:
            while wall_count[(x, y)] > 2:
                eligible_walls = self._breakable_walls(
                    maze, x, y, pattern_cells
                )

                if not eligible_walls:
                    break

                wall_direction = random.choice(eligible_walls)
                maze.remove_wall(x, y, wall_direction)
                tracks.append((x, y, wall_direction))
                wall_count[(x, y)] -= 1

        return (maze, tracks)

    def _cell_wall_count(self, x: int, y: int) -> int:
        """Return the number of walls surrounding cell (x, y) (0–4)."""
        return self.maze.grid[y][x].bit_count()

    def generate(self) -> list[tuple[int, int, str]]:
        """Generates the maze using a randomized version
        of Kruskal's algorithm."""
        random.shuffle(self._eligible_walls)
        print(len(self._eligible_walls))
        while len(self._union) > 1:
            if not self._eligible_walls:
                break
            x, y, wall_direction = self._eligible_walls[0]
            neighbor = self._get_direction_neighbor(x, y, wall_direction)
            indexes = self._find_in_union((x, y), neighbor)
            if indexes:
                self.maze.remove_wall(x, y, wall_direction)
                self._concatenate_in_union(indexes)
                self.tracks.append((x, y, wall_direction))
            neighbor_wall = neighbor + tuple(self.REVERSE.get(wall_direction))
            index = 0
            if len(self._eligible_walls) > 1:
                for i, wall in enumerate(self._eligible_walls[1:], 1):
                    if neighbor_wall == wall:
                        index = i
                        break
                self._eligible_walls.pop(index)
            self._eligible_walls.pop()
        print(len(self._union))
        return self.tracks

                    # wall_direction = random.choice(eligible_walls)
                    # neighbor = self._get_direction_neighbor(x, y, wall_direction)
                    # self.maze.remove_wall(x, y, wall_direction)
                    # self.tracks.append((x, y, wall_direction))
                    # indexes = self._find_in_union((x, y), neighbor)
                    # if indexes is not False:
                    #     self._concatenate_in_union(indexes)


# if __name__ == "__main__":
#     from view.terminal_view import TerminalView
#     algo = Kruksal(Maze(10, 10))
#     algo.generate()
#     view = TerminalView(algo.maze, exit=(9, 9), forty_two_cells=algo.forty_two_cells)
#     view.show_solution([], False, algo.tracks)
