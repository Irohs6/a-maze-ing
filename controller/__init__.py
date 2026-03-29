# controller/__init__.py — Initialisation du package controller.
# Expose la classe MazeController pour simplifier son import
# depuis le point d'entrée principal (a_maze_ing.py).

from controller.maze_controller import MazeController

__all__ = ['MazeController']
