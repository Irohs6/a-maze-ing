from __future__ import annotations
from copy import deepcopy
import time
from typing import TYPE_CHECKING
import tty
import termios
import sys
from colorama import Back, init, Style, Fore
import click
from pydantic import ValidationError
from model.config_file import ConfigFile

if TYPE_CHECKING:
    from controller.maze_controller import MazeController

init(autoreset=False)


class Menu:

    SETTINGS_FIELDS = [
        ("WIDTH", "Maze width"),
        ("HEIGHT", "Maze height"),
        ("ENTRY", "Entry position"),
        ("EXIT", "Exit position"),
        ("OUTPUT_FILE", "Output file name"),
        ("PERFECT", "Perfect maze?"),
        ("SEED", "Random seed"),
    ]

    def __init__(self, controller: MazeController):
        self._controller = controller
        self._copy_config = deepcopy(self._controller._config)
        self.fd = sys.stdin.fileno()
        self.old = termios.tcgetattr(self.fd)
        self.input = None
        self.index = 0

    def _update_objects(self):
        self._controller._create_gen()
        self._controller._create_pathfinder()
        self._controller._create_view()

    def _get_key(self):
        try:
            tty.setraw(self.fd)
            self.input = sys.stdin.read(1)
            if self.input.startswith("\x1b"):
                self.input += sys.stdin.read(2)
        finally:
            termios.tcsetattr(self.fd, termios.TCSADRAIN, self.old)

    def _move(self):
        if self.input == "\x1b[A":
            self.index = (self.index - 1) % 3
        elif self.input == "\x1b[B":
            self.index = (self.index + 1) % 3

    def _print_menu(self):
        print("╭" + "─" * 30 + "╮")
        print("│" + f"{Fore.YELLOW}A-Maze-Ing{Style.RESET_ALL}".center(39) +
              "│")
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

    def _ask_for_value(self, value: str):
        print("╭" + "─" * 30 + "╮")
        print("│" + value.center(30) + "│" + " :")
        print("╰" + "─" * 30 + "╯")

    def _settings(self):
        config = {}
        try:
            while True:
                self._ask_for_value("Enter Width")
                config["WIDTH"] = click.prompt(
                    " ", prompt_suffix="", type=click.IntRange(min=4, max=100)
                )
                print("\033c", end="")
                self._ask_for_value("Enter Height")
                config["HEIGHT"] = click.prompt(
                    " ", prompt_suffix="", type=click.IntRange(4, 100)
                )
                print("\033c", end="")
                self._ask_for_value("Enter Entry width")
                config["ENTRY"] = [
                    click.prompt(
                        " ",
                        prompt_suffix="",
                        type=click.IntRange(0, config["WIDTH"]),
                    )
                ]
                print("\033c", end="")
                self._ask_for_value("Enter Entry height")
                config["ENTRY"].append(
                    click.prompt(
                        " ",
                        prompt_suffix="",
                        type=click.IntRange(0, config["HEIGHT"]),
                    )
                )
                config["ENTRY"] = tuple(config["ENTRY"])
                print("\033c", end="")
                self._ask_for_value("Enter Exit width")
                config["EXIT"] = [
                    click.prompt(
                        " ",
                        prompt_suffix="",
                        type=click.IntRange(0, config["WIDTH"]),
                    )
                ]
                print("\033c", end="")
                self._ask_for_value("Enter Exit height")
                config["EXIT"].append(
                    click.prompt(
                        " ",
                        prompt_suffix="",
                        type=click.IntRange(0, config["HEIGHT"]),
                    )
                )
                config["EXIT"] = tuple(config["EXIT"])
                print("\033c", end="")
                self._ask_for_value("Enter Output file")
                config["OUTPUT_FILE"] = click.prompt(
                    " ", prompt_suffix="", type=str
                )
                print("\033c", end="")
                self._ask_for_value("Perfect ?")
                config["PERFECT"] = click.confirm(" ")
                print("\033c", end="")
                self._ask_for_value("Enter Seed (optional)")
                config["SEED"] = click.prompt(
                    " ",
                    prompt_suffix="",
                    type=click.IntRange(0),
                    default=time.time_ns(),
                )
                print("\033c", end="")
                try:
                    self._controller._config = ConfigFile(**config)
                except ValidationError as errors:
                    print(
                        Fore.RED
                        + "Error while creating the object, please try again"
                        + Style.RESET_ALL
                    )
                    for i, error in enumerate(errors.errors()):
                        print(
                            Fore.RED
                            + f"{i + 1}. "
                            + error["msg"]
                            + Style.RESET_ALL
                        )
                    print("Press Enter to retry...")
                    while True:
                        self._get_key()
                        if self.input == "\r":
                            break
                    print("\033c", end="")
                else:
                    self._update_objects()
                    break
        except click.exceptions.Abort:
            pass

    def _execute(self):
        if self.index == 0:
            self._controller._generator.generate()
            tracks = self._controller._generator.tracks
            paths = self._controller._finder.find_k_shortest_paths()
            is_perfect = len(paths) == 1
            self._controller._view.show_solution(
                paths,
                is_perfect,
                tracks
            )
            output = self._controller._generator.maze.encode_hex() + '\n'
            entry, exit = (str(self._controller._config.ENTRY).strip("()"),
                           str(self._controller._config.EXIT).strip("()"))
            output += entry + '\n'
            output += exit + '\n'
            for directions in paths[0].values():
                output += directions[-1]
            output = output[:-1]
            output += '\n'
            with open(self._controller._config.OUTPUT_FILE, "w") as file:
                file.write(output)
            print("Maze Output:")
            print(output, end="")
            print("Press Enter to continue...")
            while True:
                self._get_key()
                if self.input == '\r':
                    break
            self._controller._generator.reset(seed=time.time_ns())
            print("\033c", end="")
        elif self.index == 1:
            self._settings()

    def _run(self):
        try:
            while True:
                print("\033[?25l", end="")
                print("\033c", end="")
                self._print_menu()
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
