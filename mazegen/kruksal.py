import copy
import random

from .algorithm import Algorithm
from model.maze import Maze
from model.maze_validator import MazeValidator


class Kruksal(Algorithm):
    perfect: bool = False

    # Nombre maximal de tentatives globales avant d'abandonner
    _MAX_GLOBAL_ATTEMPTS: int = 10

    def generate(self) -> list[tuple[int, int, str]]:
        """Generates the maze using a randomized version
        of Kruskal's algorithm."""
        # Save the initial maze to be able to start over
        initial_maze = copy.deepcopy(self.maze)

        for _attempt in range(self._MAX_GLOBAL_ATTEMPTS):
            # Reset the maze and related attributes for a fresh attempt
            self.maze = copy.deepcopy(initial_maze)
            self.forty_two_cells = set()
            self.track = []

            tracks = []
            pattern_cells = self.maze.forty_two_cells
            pattern_neighbors = self._get_42_neighbors()

            unvisited = [
                (x, y)
                for x in range(self.width)
                for y in range(self.height)
                if (x, y) not in pattern_cells
            ]
            if not unvisited:
                continue
            i = random.randint(0, len(unvisited) - 1)
            x, y = unvisited[i]
            while unvisited:
                wall_direction = random.choice(["N", "E", "S", "W"])
                neighbor = self._get_direction_neighbor(
                    x, y, wall_direction
                )
                if (
                    (x, y) not in pattern_cells
                    and neighbor not in pattern_cells
                ):
                    try:
                        self.maze.remove_wall(x, y, wall_direction)
                    except ValueError:
                        continue
                    else:
                        tracks.append((x, y, wall_direction))
                        unvisited[i] = unvisited[-1]
                        unvisited.pop()
                if not unvisited:
                    break
                i = random.randint(0, len(unvisited) - 1)
                x, y = unvisited[i]

            def second_loop(maze: Maze) -> Maze:
                _to_destroy: set[tuple[int, int]] = {
                    (x, y)
                    for x in range(self.width)
                    for y in range(self.height)
                    if maze._cell_wall_count(x, y) > 2
                    and (x, y) not in pattern_cells
                }
                _to_destroy -= self._get_maze_boundaries()
                to_be_destroyed: list[tuple[int, int]] = list(_to_destroy)
                while to_be_destroyed:
                    i = random.randint(0, len(to_be_destroyed) - 1)
                    x, y = to_be_destroyed[i]
                    wall_direction = random.choice(["N", "E", "S", "W"])
                    if (
                        maze.has_wall(x, y, wall_direction)
                        and self._get_direction_neighbor(x, y, wall_direction)
                        not in pattern_cells
                    ):
                        try:
                            maze.remove_wall(x, y, wall_direction)
                        except ValueError:
                            continue
                        else:
                            tracks.append((x, y, wall_direction))
                            to_be_destroyed[i] = to_be_destroyed[-1]
                            to_be_destroyed.pop()
                    elif maze._cell_wall_count(x, y) <= 2:
                        to_be_destroyed = [
                            (x, y)
                            for x in range(self.width)
                            for y in range(self.height)
                            if maze._cell_wall_count(x, y) > 2
                            and (x, y) not in pattern_cells
                        ]
                    elif (x, y) in pattern_neighbors:
                        to_be_destroyed[i] = to_be_destroyed[-1]
                        to_be_destroyed.pop()
                return maze

            potential_maze = copy.deepcopy(self.maze)
            validator = MazeValidator(potential_maze)
            counter = 0
            until_now = len(tracks)
            while (
                not validator._validate_maze_connectivity()
                or validator._has_forbidden_open_areas()
            ):
                tracks = tracks[:until_now]
                potential_maze = copy.deepcopy(self.maze)
                potential_maze = second_loop(potential_maze)
                validator = MazeValidator(potential_maze)
                counter += 1
                if counter >= 33:
                    # Abandon de cette tentative, on repart de zéro
                    break
            else:
                # Le while s'est terminé sans break → maze valide trouvé
                self.maze = potential_maze
                self.track = tracks
                return tracks

        raise ValueError(
            f"Kruskal: impossible de générer un labyrinthe valide "
            f"en {self._MAX_GLOBAL_ATTEMPTS} "
            f"tentatives ({self.width}x{self.height})"
        )
