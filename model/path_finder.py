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

    def find_k_shortest_paths(
        self, k: int = 3
    ) -> list[dict[tuple[int, int], set[str]]]:
        """Retourne les k plus courts chemins sous forme de connexions par cellule.

        Chaque chemin est un dict : cellule → ensemble des directions par
        lesquelles le chemin entre/sort de cette cellule.
        Exemple : {(0,0): {'E'}, (1,0): {'W','S'}, (1,1): {'N'}}

        Ce format est directement utilisable par la vue sans conversion.
        Si la liste retournée contient exactement 1 élément, le labyrinthe
        est parfait (chemin unique).

        Args:
            k: Nombre maximum de chemins à retourner.
        """
        # Direction opposée : quand on arrive dans une cellule depuis une
        # direction, la cellule d'arrivée enregistre la direction inverse.
        REVERSE = {'N': 'S', 'S': 'N', 'E': 'W', 'W': 'E'}

        maze = self.maze
        start = self.entry
        goal = self.exit

        results: list[dict[tuple[int, int], set[str]]] = []
        # Chaque entrée de la file : (x, y, chemin_parcouru, cellules_visitées)
        queue: deque[
            tuple[int, int, list[str], frozenset[tuple[int, int]]]
        ] = deque()
        queue.append((start[0], start[1], [], frozenset({start})))

        while queue and len(results) < k:
            x, y, path, visited = queue.popleft()

            if (x, y) == goal:
                # Chemin trouvé : on construit le dict de connexions par cellule
                connections: dict[tuple[int, int], set[str]] = {}
                cx, cy = start
                connections[(cx, cy)] = set()
                for d in path:
                    connections[(cx, cy)].add(d)
                    dx, dy = self.DIRECTIONS[d]
                    cx, cy = cx + dx, cy + dy
                    if (cx, cy) not in connections:
                        connections[(cx, cy)] = set()
                    # La cellule d'arrivée enregistre la direction d'où on vient
                    connections[(cx, cy)].add(REVERSE[d])
                results.append(connections)
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
