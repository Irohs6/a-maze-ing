from typing import Any
from model.config_parser import ConfigParser
from mazegen.maze_generator import MazeGenerator
from view.terminal_view import TerminalView
from view.curse_view import CursesView


class MazeController:
    """Central orchestrator: loads config, generates maze, finds path,
     renders view."""

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
            width=self._config["WIDTH"],
            height=self._config["HEIGHT"],
            seed=self._config.get("SEED"),
            perfect=self._config.get("PERFECT", True),
            algorithm=self._config.get("ALGORITHM", "backtracker"),
        )

        # 2. Générer le labyrinthe + récupérer la trace
        self._generator.generate()
        maze = self._generator.get_maze()
        track = self._generator.track
        forty_two_cells = self._generator.forty_two_cells
        # 3. Instancier la vue
        entry = self._config.get("ENTRY", (0, 0))
        exit_pos = self._config.get("EXIT", (0, 0))
        view_mode = self._config.get("VIEW", "terminal").lower()
        if view_mode == "curse":
            view = CursesView(maze, track, entry=entry, exit=exit_pos)
            view.start()
        else:
            view = TerminalView(maze, track, entry=entry, exit=exit_pos,
                                forty_two_cells=forty_two_cells)
            if track and isinstance(track[0], tuple):
                view.play_kruksal()
            else:
                view.play()
            view.print_unicode()

        # 4. Affichage terminal de la seed
        seed_used = self._generator.seed
        print(f"\nSeed utilisée : {seed_used}")

        # 5. Écriture dans OUTPUT_FILE
        output_file = self._config.get("OUTPUT_FILE", "maze.txt")
        hex_grid = maze.encode_hex()
        with open(output_file, "w") as f:
            f.write(f"# seed={seed_used}\n")
            f.write(hex_grid)
            f.write(f"{self._config.get('ALGORITHM', 'backtracker')}\n")
            f.write(
                "activate\n" if self._config.get("PERFECT", True)
                else "deactivate\n"
            )

        print(f"Labyrinthe sauvegardé dans '{output_file}' (seed={seed_used})")
        print(hex_grid)
