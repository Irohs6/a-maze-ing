# mazegen/maze_generator.py — Module réutilisable de génération de labyrinthe.
# Contient la classe MazeGenerator, conçue pour être importée dans n'importe quel projet.
# La classe encapsule la logique complète de génération et expose une API claire :
#   - __init__(width, height, seed, perfect, algorithm) : initialise le générateur
#   - generate() : génère le labyrinthe et le stocke en interne
#   - get_maze() : retourne la grille de cellules sous forme de tableau 2D
#   - get_solution() : retourne le chemin le plus court sous forme de liste de directions
#   - reset(seed) : réinitialise et régénère avec une nouvelle graine
# Implémente au moins un algorithme de génération (ex. : recursive backtracker ou Prim)
# qui garantit les contraintes du sujet (connectivité, largeur max de couloir, motif 42).
# Contient une documentation complète avec exemples d'utilisation (conforme PEP 257).

import time
import random

from model.maze import Maze
from model.maze_validator import MazeValidator
from view.terminal_view import TerminalView
import copy


class MazeGenerator:
    """Generates a maze based on specified parameters.

    This class encapsulates the entire maze generation logic, allowing for
    easy reuse in any project. It supports multiple algorithms and ensures
    that generated mazes meet the required constraints.

    Example usage:
        generator = MazeGenerator(width=10, height=10, seed=42, perfect=True, 
        algorithm='backtracker
        generator.generate()
        maze_grid = generator.get_maze()
        solution_path = generator.get_solution()
    """

    def __init__(self, width: int, height: int, seed: int = None,
                 perfect: bool = True, algorithm: str = 'backtracker') -> None:
        """Initialize the maze generator with given parameters."""
        self.width = width
        self.height = height
        self.seed = seed
        if seed is not None:
            random.seed(seed)
        self.perfect = perfect
        self.algorithm = algorithm
        self.maze = Maze(self.width, self.height)
        self.solution_path = None
        self.track: list[str] = []
        self.pattern_42_cells = set()

    def generate(self) -> None:
        """Generate the maze using the specified algorithm."""
        if self.algorithm in ('backtracker', 'recursive_backtracker'):
            self._generate_backtracker()
        elif self.algorithm == 'kruskal':
            self._generate_kruksal()
        else:
            raise ValueError(f"Unsupported algorithm: {self.algorithm}")

        # Validate only AFTER generation
        # validator = MazeValidator(self.maze)
        # if not validator.validate():
        # raise ValueError("Generated maze is invalid.")

    def get_maze(self) -> list[list[int]]:
        """Return the generated maze grid as a 2D list of cell values."""
        return self.maze

    def get_solution(self) -> list[str]:
        """Return the solution path as a list of directions (e.g., ['N', 'E', 'S'])."""
        if self.solution_path is None:
            raise ValueError("Solution not generated yet. Call generate() first.")
        return self.solution_path

    def reset(self, seed: int = None) -> None:
        if seed is not None:
            self.seed = seed
            random.seed(seed)

        self.maze = Maze(self.width, self.height)
        self.solution_path = None
        self.track = []

    def place_42_center(self):
        maze = self.maze
        ph = len(self.maze.PATTERN_42)
        pw = len(self.maze.PATTERN_42[0])

        # Trop petit → on ne place pas
        if maze.width < pw or maze.height < ph:
            return False

        start_x = (maze.width - pw) // 2
        start_y = (maze.height - ph) // 2

        # Nouveau : set contenant toutes les cellules du motif

        # Appliquer le motif
        for dy in range(ph):
            for dx in range(pw):
                if self.maze.PATTERN_42[dy][dx] == 15:
                    x = start_x + dx
                    y = start_y + dy

                    maze.grid[y][x] = 15
                    self.pattern_42_cells.add((x, y))

        return self.pattern_42_cells

    def _generate_backtracker(self) -> list[str]:
        """Internal method to generate the maze using the recursive backtracker
         algorithm."""
        # Implementation of the backtracker algorithm goes here.
        # This method should modify self.maze to create the maze and
        # set self.solution_path to the correct path from start to finish.

        directions = {
            'N': (0, -1),
            'E': (1, 0),
            'S': (0, 1),
            'W': (-1, 0),
        }

        start = (0, 0)
        visited = self.place_42_center()
        stack = []
        track = []

        visited.add(start)
        stack.append(start)

        while stack:
            current_cell = stack[-1]
            x, y = current_cell

            neighbors = []

            for direction, (offset_x, offset_y) in directions.items():
                nx = x + offset_x
                ny = y + offset_y

                # Check boundaries
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    if (nx, ny) not in visited:
                        neighbors.append((nx, ny, direction))

            if not neighbors:
                stack.pop()
                track.append("BACK")
                continue
            else:
                nx, ny, direction = random.choice(neighbors)
                self.maze.remove_wall(x, y, direction)
                visited.add((nx, ny))
                stack.append((nx, ny))
                track.append(direction)

        self.track = track
        return track

    def _generate_kruksal(self):
        tracks = []
        initial_maze = copy.deepcopy(self.maze)
        total = self.height * self.width
        reached = 1
        x = random.randint(0, self.width - 1)
        y = random.randint(0, self.height - 1)
        unvisited = [(x, y) for x in range(self.width) for y in range(self.height)]
        while (reached < total):
            wall_direction = random.choice(['N', 'E', 'S', 'W'])
            try:
                self.maze.remove_wall(x, y, wall_direction)
            except ValueError:
                continue
            else:
                reached += 1
                tracks.append((x, y, wall_direction))
            if reached == total:
                break
            i = random.randint(0, len(unvisited) - 1)
            x, y = unvisited[i]
            unvisited[i] = unvisited[-1]
            unvisited.pop()

        def second_loop(maze):
            nonlocal tracks
            to_be_destroyed = {(x, y) for x in range(self.width) for y in range(self.height) if maze._cell_wall_count(x, y) > 2}
            to_be_destroyed -= self.maze._get_maze_boundaries()
            to_be_destroyed = list(to_be_destroyed)
            while to_be_destroyed:
                i = random.randint(0, len(to_be_destroyed) - 1)
                x, y = to_be_destroyed[i]
                wall_direction = random.choice(['N', 'E', 'S', 'W'])
                if maze.has_wall(x, y, wall_direction):
                    try:
                        maze.remove_wall(x, y, wall_direction)
                    except ValueError:
                        continue
                    else:
                        tracks.append((x, y, wall_direction))
                        to_be_destroyed[i] = to_be_destroyed[-1]
                        to_be_destroyed.pop()
                        # neighbor = None
                        # for nx, ny, direction in self.maze._get_neighbors_of_cell(x, y):
                        #     if direction == wall_direction:
                        #         neighbor = (nx, ny)
                        #         break

                        # # 🔑 mettre à jour le voisin si besoin
                        # if neighbor:
                        #     if maze._cell_wall_count(*neighbor) <= 2:
                        #         if neighbor in to_be_destroyed:
                        #             j = to_be_destroyed.index(neighbor)
                        #             to_be_destroyed[j] = to_be_destroyed[-1]
                        #             to_be_destroyed.pop()

                elif maze._cell_wall_count(x, y) <= 2:
                    to_be_destroyed = [(x, y) for x in range(self.width) for y in range(self.height) if maze._cell_wall_count(x, y) > 2]
            return maze
        potential_maze = copy.deepcopy(self.maze)
        validator = MazeValidator(potential_maze)
        counter = 0
        until_now = len(tracks)
        while not validator._validate_maze_connectivity() or validator._has_forbidden_open_areas():
            tracks = tracks[:until_now]
            potential_maze = copy.deepcopy(self.maze)
            potential_maze = second_loop(potential_maze)
            validator = MazeValidator(potential_maze)
            counter += 1
            if counter == 33:
                self.maze = initial_maze
                self.tracks = self._generate_kruksal()
        self.maze = potential_maze
        self.track = tracks
        return tracks


if __name__ == "__main__":
    generator = MazeGenerator(15, 15, perfect=False)
    start = time.time()
    tracks = generator._generate_kruksal()
    # Entrée et sortie par défaut (0,0) et (width-1, height-1)
    entry = (0, 0)
    exit_pos = (generator.width - 1, generator.height - 1)
    view = TerminalView(generator.get_maze(), tracks, entry=entry, exit=exit_pos)
    view.play_kruksal()
    view.print_unicode()
    print(f"TIME: {round(time.time() - start, 2)} seconds")
