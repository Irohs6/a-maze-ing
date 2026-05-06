# view/__init__.py — Initialization of the view package.
# Exposes available rendering classes (TerminalView and optionally
# MlxView) so the controller can instantiate them without knowing
# the internal organisation of the package. May contain a factory
# to choose the display mode based on configuration or program arguments.

from .terminal_view import TerminalView
# from .mlx_view import MlxView  # Uncomment if MlxView is implemented

__all__ = ['TerminalView']  # Add 'MlxView' if implemented
