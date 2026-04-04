# model/path_finder.py — Algorithme de recherche du chemin le plus court.
# Contient la classe PathFinder qui opère sur une instance de Maze.
# Implémente un algorithme BFS (Breadth-First Search) pour trouver
# le chemin valide le plus court entre l'entrée et la sortie.
# Fournit des méthodes pour :
#   - calculer et retourner le chemin sous forme de liste de directions
#     (N, E, S, W)
#   - vérifier l'accessibilité globale du labyrinthe
#     (toutes les cellules atteignables)
#   - vérifier l'unicité du chemin si PERFECT=True
# Le résultat est utilisé à la fois pour l'écriture dans le fichier de sortie
# et pour l'affichage visuel de la solution.

from __future__ import annotations

from collections import deque
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from model.maze import Maze


class PathFinder:
    """Find the shortest path through a maze using BFS.

    Operates on a Maze instance and uses breadth-first search to find the
    valid shortest path from entry to exit. Also provides methods to check
    global accessibility and path uniqueness.

    Example usage:
        path_finder = PathFinder(maze, entry=(0, 0), exit=(19, 14))
        solution_path = path_finder.find_path()
    """

    DIRECTIONS: dict[str, tuple[int, int]] = {
        'N': (0, -1),
        'E': (1, 0),
        'S': (0, 1),
        'W': (-1, 0),
    }

    def __init__(
        self,
        maze: Maze,
        entry: tuple[int, int],
        exit: tuple[int, int],
    ) -> None:
        """Initialize with a Maze instance and entry/exit coordinates."""
        self.maze = maze
        self.entry = entry
        self.exit = exit

    def find_path(self) -> list[str]:
        """Return the shortest path from entry to exit as direction labels.

        Returns:
            A list of directions (N, E, S, W) representing the path.
            Returns an empty list if no path exists.
        """
        paths = self.find_k_shortest_paths(k=1)
        return paths[0] if paths else []

    def find_k_shortest_paths(self, k: int = 3) -> list[list[str]]:
        """Return the k shortest simple paths from entry to exit.

        Uses BFS with per-path visited tracking to enumerate simple paths
        in ascending order of length. Returns fewer than k paths if fewer exist.

        Args:
            k: Maximum number of paths to return.

        Returns:
            List of up to k paths, each a list of directions (N, E, S, W).
        """
        maze = self.maze
        start = self.entry
        goal = self.exit

        results: list[list[str]] = []
        # Each entry: (x, y, path_so_far, visited_cells)
        queue: deque[
            tuple[int, int, list[str], frozenset[tuple[int, int]]]
        ] = deque()
        queue.append((start[0], start[1], [], frozenset({start})))

        while queue and len(results) < k:
            x, y, path, visited = queue.popleft()

            if (x, y) == goal:
                results.append(path)
                continue

            for direction, (dx, dy) in self.DIRECTIONS.items():
                if maze.has_wall(x, y, direction):
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < maze.width and 0 <= ny < maze.height:
                    pos = (nx, ny)
                    if pos not in visited:
                        queue.append((
                            nx, ny,
                            path + [direction],
                            visited | {pos},
                        ))

        return results

    def has_unique_path(self) -> bool:
        """Return True if exactly one path exists from entry to exit.

        Detects cycles reachable from entry using BFS parent tracking.
        A cycle means multiple paths exist between some pair of cells,
        so this is only meaningful when PERFECT=True.
        """
        maze = self.maze
        start = self.entry
        goal = self.exit

        parent: dict[tuple[int, int], tuple[int, int] | None] = {start: None}
        queue: deque[tuple[int, int]] = deque([start])

        while queue:
            x, y = queue.popleft()
            for direction, (dx, dy) in self.DIRECTIONS.items():
                if maze.has_wall(x, y, direction):
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < maze.width and 0 <= ny < maze.height:
                    neighbor = (nx, ny)
                    if neighbor not in parent:
                        parent[neighbor] = (x, y)
                        queue.append(neighbor)
                    elif parent[(x, y)] != neighbor:
                        # Cross-edge found → cycle → multiple paths
                        return False

        return goal in parent
