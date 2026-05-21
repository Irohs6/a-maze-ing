from __future__ import annotations
from copy import deepcopy
import time
from typing import TYPE_CHECKING
import tty
import termios
import sys
try:
    from colorama import Back, init, Style, Fore
except ImportError:
    print("\033c", end="")
    print(
        "Colorama not found, try starting the program with 'make run' command."
    )
    sys.exit(7)
try:
    import click
except ImportError:
    print("\033c", end="")
    print(
        "Click not found, try starting the program with 'make run' command."
    )
    sys.exit(7)
try:
    from pydantic import ValidationError
except ImportError:
    print("\033c", end="")
    print(
        "Pydantic not found, try starting the program with 'make run' command."
    )
    sys.exit(7)

if TYPE_CHECKING:
    from ..controller.maze_controller import MazeController

init(autoreset=False)


class Menu:
    """Interactive terminal menu for maze generation and settings."""

    SETTINGS_FIELDS = [
        "WIDTH",
        "HEIGHT",
        "ENTRY",
        "EXIT",
        "OUTPUT_FILE",
        "PERFECT",
        "SEED",
        "ALGORITHM",
    ]

    def __init__(self, controller: MazeController) -> None:
        """Initialize the menu with the given controller."""
        self._controller = controller
        self.copy_config = deepcopy(self._controller._config)
        self.fd = sys.stdin.fileno()
        self.old = termios.tcgetattr(self.fd)
        self.input: str = ""
        self.index = 0
        self.len_menu = [3, 9]
        self.current_menu = 0

    def _update_objects(self) -> None:
        """Rebuild the generator, pathfinder, cycle checker, and view."""
        self._controller._create_gen()
        self._controller._create_pathfinder()
        self._controller._create_cycles_checker()
        self._controller._create_view()

    def _get_key(self) -> None:
        """Read a single key (or escape sequence) from stdin."""
        try:
            tty.setraw(self.fd)
            self.input = sys.stdin.read(1)
            if self.input.startswith("\x1b"):
                self.input += sys.stdin.read(2)
        finally:
            termios.tcsetattr(self.fd, termios.TCSADRAIN, self.old)

    def _move(self) -> None:
        """Update the cursor index based on arrow-key input."""
        if self.input == "\x1b[A":
            self.index = (self.index - 1) % self.len_menu[self.current_menu]
        elif self.input == "\x1b[B":
            self.index = (self.index + 1) % self.len_menu[self.current_menu]

    def _print_base_menu(self) -> None:
        """Render the main menu to stdout."""
        print("╭" + "─" * 30 + "╮")
        print(
            "│" + f"{Fore.YELLOW}A-Maze-Ing{Style.RESET_ALL}".center(39) + "│"
        )
        print("├" + "─" * 30 + "┤")
        for i, option in enumerate(
            [" Generate  Maze ", " Settings ", " Exit "]
        ):
            center = 30
            print("│", end="")
            if i == self.index:
                option = Back.RED + option + Style.RESET_ALL
                center = 39
            print(option.center(center), end="")
            print("│")
        print("╰" + "─" * 30 + "╯")

    def _press_enter_continue(self) -> None:
        """Block until the user presses Enter."""
        print("\nPress Enter to continue...")
        while True:
            self._get_key()
            if self.input == "\r":
                break

    def _print_settings_menu(self) -> None:
        """Render the settings menu to stdout."""
        if self._controller._config is None:
            raise RuntimeError("Config not initialized")
        if self._controller._generator is None:
            raise RuntimeError("Generator not initialized")
        options = [
            f"Width (current: {self._controller._config.WIDTH})",
            f"Height (current: {self._controller._config.HEIGHT})",
            f"Entry (current: {self._controller._config.ENTRY})",
            f"Exit (current: {self._controller._config.EXIT})",
            "Output File (current: "
            f"{self._controller._config.OUTPUT_FILE})",
            f"Perfect (current: {self._controller._config.PERFECT})",
            f"Seed (current: {self._controller._generator.seed})",
            f"Algorithm (current: {self._controller._config.ALGORITHM})",
            "Go  Back",
        ]
        max_len = len(max(options, key=lambda option: len(option)))
        max_len += 10 if max_len % 2 == 0 else 11
        print("╭" + "─" * max_len + "╮")
        print(
            "│"
            + f"{Fore.RED}Settings{Style.RESET_ALL}".center(max_len + 9)
            + "│"
        )
        print("├" + "─" * max_len + "┤")
        for i, option in enumerate(options):
            center = max_len
            print("│", end="")
            if i == self.index:
                if len(option) % 2 == 1:
                    option += " "
                center = max_len + 9
                option = Back.RED + option + Style.RESET_ALL
            print(option.center(center), end="")
            print("│")
        print("╰" + "─" * max_len + "╯")

    def _ask_for_value(self, value: str) -> None:
        """Display a prompt box asking for a value."""
        print("╭" + "─" * 30 + "╮")
        print("│" + value.center(30) + "│" + " :")
        print("╰" + "─" * 30 + "╯")

    def _change_setting(self) -> None:
        """Prompt the user to change the currently selected setting."""
        if self._controller._config is None:
            raise RuntimeError("Config not initialized")
        try:
            field = self.SETTINGS_FIELDS[self.index]
            if self.index < 2:
                self._ask_for_value(f"Enter {field}")
                dimension = click.prompt(
                    " ", prompt_suffix="", type=click.IntRange(min=4, max=100)
                )
                setattr(self._controller._config, field, dimension)
            elif self.index < 4:
                while True:
                    click.clear()
                    self._ask_for_value(f"Enter {field} Width:")
                    width = click.prompt(
                        " ",
                        prompt_suffix="",
                        type=click.IntRange(
                            min=0, max=self._controller._config.WIDTH - 1
                        ),
                    )
                    click.clear()
                    self._ask_for_value(f"Enter {field} Height:")
                    height = click.prompt(
                        " ",
                        prompt_suffix="",
                        type=click.IntRange(
                            min=0, max=self._controller._config.HEIGHT - 1
                        ),
                    )
                    try:
                        setattr(
                            self._controller._config, field, (width, height)
                        )
                    except ValidationError:
                        continue
                    else:
                        break
            elif self.index == 4:
                self._ask_for_value(f"Enter {field}")
                output_file = click.prompt(" ", prompt_suffix="", type=str)
                setattr(self._controller._config, field, output_file)
            elif self.index == 5:
                self._ask_for_value(f"{field} ?")
                perfect_bool = click.confirm(" ")
                setattr(self._controller._config, field, perfect_bool)
            elif self.index == 6:
                self._ask_for_value(f"Enter {field}")
                seed = click.prompt(
                    " ",
                    prompt_suffix="",
                    type=click.IntRange(0),
                    default=time.time_ns(),
                )
                setattr(self._controller._config, field, seed)
            elif self.index == 7:
                self._ask_for_value(f"Choose {field}")
                algo = click.prompt(
                    " ",
                    prompt_suffix="",
                    type=click.Choice(
                        ["kruksal", "backtracker"], case_sensitive=False
                    ),
                )
                setattr(self._controller._config, field, algo)
        except ValidationError as error:
            self._controller._config = deepcopy(self.copy_config)
            print(error)
            self._press_enter_continue()
        except click.exceptions.Abort:
            pass
        else:
            try:
                self._update_objects()
            except ValueError as error:
                self._controller._config = deepcopy(self.copy_config)
                self._update_objects()
                print(error)
                self._press_enter_continue()
            else:
                self.copy_config = deepcopy(self._controller._config)

    def _settings_menu(self) -> None:
        """Run the settings submenu loop."""
        try:
            while True:
                print("\033[?25l", end="")
                self._print_settings_menu()
                self._get_key()
                if self.input.startswith("\x1b"):
                    self._move()
                elif self.input == "\r":
                    if self.index == 8:
                        break
                    else:
                        print("\033[?25h", end="")
                        print("\033c", end="")
                        self._change_setting()
                print("\033c", end="")
        finally:
            self.index = 1
            self.current_menu = 0

    def _generate_maze(self) -> None:
        """Generate a maze and display it, writing the result
             to the output file."""
        if self._controller._generator is None:
            raise RuntimeError("Generator not initialized")
        if self._controller._finder is None:
            raise RuntimeError("PathFinder not initialized")
        if self._controller._cycle_checker is None:
            raise RuntimeError("CycleChecker not initialized")
        if self._controller._config is None:
            raise RuntimeError("Config not initialized")
        self._controller._generator.generate()
        tracks = self._controller._generator.tracks
        path = self._controller._finder.shortest_path()
        if path:
            paths = self._controller._finder._build_connections(path)
            is_perfect = not self._controller._cycle_checker.has_cycle()
            if is_perfect != self._controller._config.PERFECT:
                print(
                    Fore.RED
                    + ('Imperfect' if not self._controller._config.PERFECT
                        else 'Perfect') + " maze could not be generated..."
                    + Style.RESET_ALL
                )
                print(f"Cursed Seed: {self._controller._generator.seed}")
                self._press_enter_continue()
                self._controller._generator.reset(seed=time.time_ns())
                print("\033c", end="")
            else:
                self._controller._view.draw_grid(tracks, paths, is_perfect)
                output = self._controller._generator.maze.encode_hex() + "\n"
                entry, exit = (
                    str(self._controller._config.ENTRY).strip("()"),
                    str(self._controller._config.EXIT).strip("()"),
                )
                output += f"Seed: {self._controller._generator.seed}" + "\n"
                output += f"Entry: {entry}" + "\n"
                output += f"Exit: {exit}" + "\n"
                output += "Solution: "
                for direction in path:
                    output += direction
                output += "\n"
                output += f"Perfect: {is_perfect}" + "\n"
                print("Maze Output:")
                print(output, end="")
                try:
                    with open(
                        self._controller._config.OUTPUT_FILE, "w"
                    ) as file:
                        file.write(output)
                except PermissionError:
                    raise PermissionError(
                        Fore.RED
                        + "Error: You don't have the permission to write in "
                        "the "
                        "output file" + Style.RESET_ALL
                    )
                except OSError as e:
                    raise OSError(
                        Fore.RED
                        + f"Error: Could not write output file: {e}"
                        + Style.RESET_ALL
                    )
                self._press_enter_continue()
                self._controller._generator.reset(seed=time.time_ns())
                print("\033c", end="")

    def _execute(self) -> None:
        """Dispatch to the action selected in the main menu."""
        if self.index == 0:
            self._generate_maze()
        elif self.index == 1:
            self.current_menu = 1
            self._settings_menu()

    def _run(self) -> None:
        """Run the main menu loop until the user exits."""
        try:
            while True:
                print("\033[?25l", end="")
                print("\033c", end="")
                self._print_base_menu()
                self._get_key()
                if self.input.startswith("\x1b"):
                    self._move()
                elif self.input == "\r":
                    print("\033c", end="")
                    print("\033[?25h", end="")
                    if self.index == 2:
                        break
                    self._execute()
        finally:
            print("\033[?25h", end="")
