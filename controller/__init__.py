# controller/__init__.py — Initialization of the controller package.
# Exposes MazeController to simplify its import
# from the main entry point (a_maze_ing.py).

from controller.maze_controller import MazeController

__all__ = ['MazeController']
