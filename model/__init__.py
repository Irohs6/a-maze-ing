# model/__init__.py — Initialisation du package model.
# Expose les classes principales du modèle pour simplifier les imports
# depuis les autres couches (contrôleur, tests) :
# Maze, ConfigParser et PathFinder sont rendus accessibles
# directement via "from model import ...".
from .config_parser import ConfigParser

__all__ = ['ConfigParser']
