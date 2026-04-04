from typing import Any
from model.config_parser import ConfigParser
from model.path_finder import PathFinder
from mazegen.maze_generator import MazeGenerator
from view.terminal_view import TerminalView


class MazeController:
    """Central orchestrator: loads config, generates maze, finds path,
     renders view."""

    def __init__(self, config_file: str) -> None:
        self._config_file: str = config_file
        self._config: dict[str, Any] = {}
        self._generator: MazeGenerator | None = None

    def _load_config(self) -> None:
        self._config = ConfigParser(self._config_file).parse()

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
        # 3. Calculer le chemin solution
        entry = self._config.get("ENTRY", (0, 0))
        exit_pos = self._config.get("EXIT", (0, 0))
        finder = PathFinder(maze, entry=entry, exit=exit_pos)
        path_dirs = finder.find_path()

        # Calculer les k plus courts chemins + détecter si parfait
        is_perfect = finder.has_unique_path()
        all_paths_dirs = finder.find_k_shortest_paths(k=3)

        # Connexions initiales pour le premier chemin
        path_connections = TerminalView._dirs_to_connections(
            path_dirs, entry
        )

        # 4. Instancier la vue
        view = TerminalView(maze, track, entry=entry, exit=exit_pos,
                            forty_two_cells=forty_two_cells,
                            path_connections=path_connections)
        if track and isinstance(track[0], tuple):
            view.play_kruksal()
        else:
            view.play()
        view.show_solution(all_paths_dirs, is_perfect)

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
