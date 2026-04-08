
from model.path_finder import PathFinder
from mazegen.maze_generator import MazeGenerator
from view.terminal_view import TerminalView
from model.config_file import ConfigFile


class MazeController:
    """Central orchestrator: loads config, generates maze, finds path,
     renders view."""

    def __init__(self, config_file: str) -> None:
        self._config_file: str = config_file
        self._config: ConfigFile | None = None
        self._generator: MazeGenerator | None = None

    def _load_config(self) -> None:
        self._config = ConfigFile.parse(self._config_file)

    def run(self) -> None:
        """Execute the full maze pipeline."""
        self._load_config()

        # 1. Instancier le générateur
        self._generator = MazeGenerator(
            width=self._config.WIDTH,
            height=self._config.HEIGHT,
            seed=self._config.SEED,
            perfect=self._config.PERFECT,
        )

        # 2. Générer le labyrinthe + récupérer la trace
        self._generator.generate()
        maze = self._generator.get_maze()
        track = self._generator.track
        forty_two_cells = self._generator.forty_two_cells
        # 3. Calculer le chemin solution
        entry = self._config.ENTRY
        exit_pos = self._config.EXIT
        finder = PathFinder(maze, entry=entry, exit=exit_pos)

        # Un seul appel suffit : si len == 1 → parfait (chemin unique)
        all_paths_dirs = finder.find_k_shortest_paths(k=3)
        is_perfect = len(all_paths_dirs) == 1

        # 4. Instancier la vue
        view = TerminalView(maze, track, entry=entry, exit=exit_pos,
                            forty_two_cells=forty_two_cells)
        # view.play()
        view.show_solution(all_paths_dirs, is_perfect, track)

        # 4. Affichage terminal de la seed
        seed_used = self._generator.seed
        print(f"\nSeed utilisée : {self._config.SEED} → {seed_used}")

        # 5. Écriture dans OUTPUT_FILE
        output_file = self._config.OUTPUT_FILE
        hex_grid = maze.encode_hex()
        with open(output_file, "w") as f:
            f.write(f"# seed={seed_used}\n")
            f.write(hex_grid)
            f.write(
                "activate\n" if self._config.PERFECT
                else "deactivate\n"
            )
        print(f"Labyrinthe sauvegardé dans '{output_file}' (seed={seed_used})")
        print(hex_grid)
