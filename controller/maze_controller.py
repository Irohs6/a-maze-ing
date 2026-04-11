
from model.path_finder import PathFinder
from mazegen.maze_generator import MazeGenerator
from view.terminal_view import TerminalView
from model.config_file import ConfigFile
from view.menu import Menu


class MazeController:
    """Central orchestrator: loads config, generates maze, finds path,
     renders view."""

    def __init__(self, config_file: str) -> None:
        self._config_file: str = config_file
        self._config: ConfigFile | None = None
        self._generator: MazeGenerator | None = None

    def _load_config(self) -> None:
        self._config = ConfigFile.parse(self._config_file)

    def _create_gen(self):
        self._generator = MazeGenerator(
            width=self._config.WIDTH,
            height=self._config.HEIGHT,
            seed=self._config.SEED,
            perfect=self._config.PERFECT
        )

    def _create_pathfinder(self):
        maze = self._generator.get_maze()
        entry = self._config.ENTRY
        exit_pos = self._config.EXIT
        self._finder = PathFinder(maze, entry=entry, exit=exit_pos)

    def _create_view(self):
        maze = self._generator.get_maze()
        entry = self._config.ENTRY
        exit_pos = self._config.EXIT

        self._view = TerminalView(maze, entry=entry, exit=exit_pos)

    def run(self) -> None:
        """Execute the full maze pipeline."""
        self._load_config()
        self.menu = Menu(self)
        self.menu._run()
