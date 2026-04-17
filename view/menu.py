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

if TYPE_CHECKING:
    from controller.maze_controller import MazeController

init(autoreset=False)


class Menu:

    SETTINGS_FIELDS = [
        "WIDTH",
        "HEIGHT",
        "ENTRY",
        "EXIT",
        "OUTPUT_FILE",
        "PERFECT",
        "SEED"
    ]

    def __init__(self, controller: MazeController):
        self._controller = controller
        self.copy_config = deepcopy(self._controller._config)
        self.fd = sys.stdin.fileno()
        self.old = termios.tcgetattr(self.fd)
        self.input = None
        self.index = 0
        self.len_menu = [3, 8]
        self.current_menu = 0

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
            self.index = (self.index - 1) % self.len_menu[self.current_menu]
        elif self.input == "\x1b[B":
            self.index = (self.index + 1) % self.len_menu[self.current_menu]

    def _print_base_menu(self):
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

    def _print_settings_menu(self):
        print("╭" + "─" * 40 + "╮")
        print("│" + f"{Fore.RED}Settings{Style.RESET_ALL}".center(49) +
              "│")
        print("├" + "─" * 40 + "┤")
        for i, option in  enumerate(
            [f"Width (current:  {self._controller._config.WIDTH})", f"Height (current: {self._controller._config.HEIGHT})", f"Entry (current:  {self._controller._config.ENTRY})", f"Exit (current: {self._controller._config.EXIT})", f"Output File (current:  {self._controller._config.OUTPUT_FILE})", f"Perfect (current: {self._controller._config.PERFECT})", f"Seed (current:  {self._controller._config.SEED})", "Go  Back"]
        ):
            center = 40
            print("│", end="")
            if i == self.index:
                center = 49
                option = Back.RED + option + Style.RESET_ALL
            print(option.center(center), end="")
            print("│")
        print("╰" + "─" * 40 + "╯")

    def _ask_for_value(self, value: str):
        print("╭" + "─" * 30 + "╮")
        print("│" + value.center(30) + "│" + " :")
        print("╰" + "─" * 30 + "╯")

    def _change_setting(self):
        try:
            field = self.SETTINGS_FIELDS[self.index]
            if self.index < 2:
                self._ask_for_value(f"Enter {field}")
                dimension = click.prompt(" ", prompt_suffix="", type=click.IntRange(min=4, max=100))
                setattr(self._controller._config, field,  dimension)
            elif self.index < 4:
                while True:
                    click.clear()
                    self._ask_for_value(f"Enter {field} Width:")
                    width = click.prompt(" ", prompt_suffix="", type=click.IntRange(min=4, max=self._controller._config.WIDTH - 1))
                    click.clear()
                    self._ask_for_value(f"Enter {field} Height:")
                    height = click.prompt(" ", prompt_suffix="", type=click.IntRange(min=4, max=self._controller._config.HEIGHT - 1))
                    try:
                        setattr(self._controller._config, field, (width, height))
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
                self._ask_for_value(f"Enter {field} (optional)")
                seed = click.prompt(
                        " ",
                        prompt_suffix="",
                        type=click.IntRange(0),
                        default=time.time_ns(),
                    )
                setattr(self._controller._config, field, seed)
        except ValidationError as error:
            self._controller._config = deepcopy(self.copy_config)
            print(error)
            print("\nPress Enter to continue...")
            while True:
                self._get_key()
                if self.input == '\r':
                    break
        except click.exceptions.Abort:
            pass
        else:
            self.copy_config = deepcopy(self._controller._config)
            self._update_objects()

    def _settings_menu(self):
        try:
            while True:
                print("\033[?25l", end="")
                self._print_settings_menu()
                self._get_key()
                if self.input.startswith("\x1b"):
                    self._move()
                elif self.input == '\r':
                    if self.index == 7:
                        break
                    else:
                        print("\033[?25h", end="")
                        print("\033c", end="")
                        self._change_setting()
                print("\033c", end="")
        finally:
            self.index = 1
            self.current_menu = 0

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
            self.current_menu = 1
            self._settings_menu()

    def _run(self):
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
