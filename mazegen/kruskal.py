import random
from .algorithm import Algorithm


class Kruskal(Algorithm):
    REVERSE: dict[str, str] = {"N": "S", "S": "N", "E": "W", "W": "E"}
    # Maximum number of global attempts before giving up

    def _get_eligible_walls(self) -> list[tuple[int, int, str]]:
        self._eligible_walls = {}
        directions = ["N", "E", "S", "W"]
        for y in range(self.height):
            for x in range(self.width):
                self._eligible_walls[(x, y)] = []
                for direction in directions:
                    if not self.maze._is_border_wall(
                        x, y, direction
                    ) and not self._is_42_wall(x, y, direction):
                        self._eligible_walls[(x, y)].append((x, y, direction))
        return self._eligible_walls

    def _find_root(self, cell: tuple[int, int]) -> tuple[int, int]:
        potential_chief = self._indexes[cell]
        while potential_chief != self._indexes[potential_chief]:
            potential_chief = self._indexes[potential_chief]
        return potential_chief

    def _find_in_union(
        self, walls
    ) -> bool:
        """Return the indexes of the sets in the union list that
        contain the given coordinates and neighbor."""
        _to_break = []
        for wall in walls:
            if self._find_root((wall[0], wall[1])) != self._find_root(self._get_direction_neighbor(*wall)):
                _to_break.append(wall)
        return _to_break

    def _concatenate_in_union(
        self, coordinates: tuple[int, int], neighbor: tuple[int, int]
    ) -> None:
        """Merge the two sets at the given indexes in the union list."""
        neighbor_root = self._find_root(neighbor)
        self._union[self._find_root(coordinates)].update(self._union[neighbor_root])
        self._union.pop(neighbor_root)
        self._indexes[self._find_root(neighbor)] = self._find_root(coordinates)

    def generate(self) -> list[tuple[int, int, str]]:
        """Generates the maze using a randomized version
        of Kruskal's algorithm."""
        _eligible_walls = self._get_eligible_walls()

        while len(self._union) > 1:
            x, y = self._cells.pop()
            _to_break = self._find_in_union(_eligible_walls[(x, y)])
            if _to_break:
                while _to_break != []:
                    x, y, direction = _to_break[0]
                    nx, ny = self._get_direction_neighbor(x, y, direction)
                    self.maze.remove_wall(x, y, direction)
                    self._concatenate_in_union((x, y), (nx, ny))
                    self.tracks.append((x, y, direction))
                    opposite_direction = self.REVERSE[direction]
                    try:
                        _eligible_walls[(nx, ny)].remove((nx, ny, opposite_direction))
                    except ValueError:
                        pass
                    _to_break = self._find_in_union(_eligible_walls[(x, y)])
        if self.is_perfect is False:
            # Call second loop to break a 15% additional
            # walls for an imperfect maze
            self.second_loop()

        return self.tracks
