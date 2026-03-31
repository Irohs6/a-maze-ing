from typing import Any
from model.config_parser import ConfigParser
from mazegen.maze_generator import MazeGenerator
from view.terminal_view import TerminalView


class MazeController:
    """Central orchestrator: loads config, generates maze, finds path, renders view."""

    def __init__(self, config_file: str) -> None:
        self._config_file: str = config_file
        self._config: dict[str, Any] = {}
        self._generator: MazeGenerator | None = None

    def _load_config(self) -> None:
        parser = ConfigParser(self._config_file)
        parser.parse()
        parser._validate_required_keys()
        parser._parse_coordinates()
        self._config = parser._get_config()

    def run(self) -> None:
        """Execute the full maze pipeline."""
        self._load_config()

        # 1. Instancier le générateur
        self._generator = MazeGenerator(
            width=self._config['WIDTH'],
            height=self._config['HEIGHT'],
            seed=self._config.get('SEED'),
            perfect=self._config.get('PERFECT', True),
            algorithm=self._config.get('ALGORITHM', 'backtracker')
        )

        # 2. Générer le labyrinthe + récupérer la trace
        track = self._generator._generate_backtracker()
        maze = self._generator.get_maze()

        # 3. Instancier la vue
        view = TerminalView(maze, track)

        # 4. Jouer l’animation de génération
        view.play()

        # 5. Afficher le labyrinthe final
        view.print_unicode()

        # 6. Encoder en hex
        print(maze.encode_hex())
