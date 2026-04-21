
from model.path_finder import PathFinder
from model.cycle_cheker import Cycle_Checker
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
        self._cycle_checker: Cycle_Checker | None = None
        self._finder: PathFinder | None = None

    def _load_config(self) -> None:
        self._config = ConfigFile.parse(self._config_file)

    def _create_gen(self) -> None:
        """Instantiate the maze generator based on the configuration."""
        self._generator = MazeGenerator(
            width=self._config.WIDTH,
            height=self._config.HEIGHT,
            perfect=self._config.PERFECT,
            seed=self._config.SEED,
            algorithm=self._config.ALGORITHM
        )

    def _create_pathfinder(self) -> None:
        """Instantiate the pathfinder based on the generated maze and config."""
        maze = self._generator.get_maze()
        entry = self._config.ENTRY
        exit_pos = self._config.EXIT
        self._finder = PathFinder(maze, entry=entry, exit=exit_pos)

    def _create_cycles_checker(self) -> None:
        """Instantiate the cycle checker based on the generated maze."""
        maze = self._generator.get_maze()
        self._cycle_checker = Cycle_Checker(maze)

    def _create_view(self) -> None:
        """Instantiate the view based on the generated maze and config."""
        maze = self._generator.get_maze()
        entry = self._config.ENTRY
        exit_pos = self._config.EXIT

        self._view = TerminalView(maze, entry=entry, exit=exit_pos,
                                  forty_two_cells=maze.forty_two_cells)

    def run(self) -> None:
        """Execute the full maze pipeline."""
        self._load_config()
        self._create_gen()
        self._create_pathfinder()
        self._create_view()
        self._create_cycles_checker()
        self.menu = Menu(self)
        self.menu._run()
