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
    def __init__(self, controller: MazeController):
        self._controller = controller
        self._copy_config = deepcopy(self._controller._config)
        self.fd = sys.stdin.fileno()
        self.old = termios.tcgetattr(self.fd)
        self.input = None
        self.index = 0

    def _update_objects(self):
        self._controller._create_objects()

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
        print("│" + "A-Maze-Ing".center(30) + "│")
        print("├" + "─" * 30 + "┤")
        for i, option in enumerate([' Generate  Maze ', ' Settings ', ' Exit ']):
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
                config['WIDTH'] = click.prompt(" ", prompt_suffix="", type=click.IntRange(min=4, max=100))
                print("\033c")
                self._ask_for_value("Enter Height")
                config['HEIGHT'] = click.prompt(" ", prompt_suffix="", type=click.IntRange(4, 100))
                print("\033c")
                self._ask_for_value("Enter Entry width")
                config['ENTRY'] = [click.prompt(" ", prompt_suffix="", type=click.IntRange(0, config['WIDTH']))]
                print("\033c")
                self._ask_for_value("Enter Entry height")
                config['ENTRY'].append(click.prompt(" ", prompt_suffix="", type=click.IntRange(0, config['HEIGHT'])))
                config['ENTRY'] = tuple(config['ENTRY'])
                print("\033c")
                self._ask_for_value("Enter Exit width")
                config['EXIT'] = [click.prompt(" ", prompt_suffix="", type=click.IntRange(0, config['WIDTH']))]
                print("\033c")
                self._ask_for_value("Enter Exit height")
                config['EXIT'].append(click.prompt(" ", prompt_suffix="", type=click.IntRange(0, config['HEIGHT'])))
                config['EXIT'] = tuple(config['EXIT'])
                print("\033c")
                self._ask_for_value("Enter Output file")
                config['OUTPUT_FILE'] = click.prompt(" ", prompt_suffix="", type=str)
                print("\033c")
                self._ask_for_value("Perfect ?")
                config['PERFECT'] = click.confirm(" ")
                print("\033c")
                self._ask_for_value("Enter Seed (optional)")
                config['SEED'] = click.prompt(" ", prompt_suffix="", type=click.IntRange(0), default=time.time_ns())
                print("\033c")
                try:
                    self._controller._config = ConfigFile(**config)
                except ValidationError:
                    print(Fore.RED + "Error while creating the object, please try again." + Style.RESET_ALL)
                    time.sleep(3)
                    print("\033c")
                else:
                    self._update_objects()
                    break
        except click.exceptions.Abort as error:
            print(error)

    def _execute(self):
        if self.index == 0:
            self._controller._generator.generate()
            tracks = self._controller._generator.track
            paths = self._controller._finder.find_k_shortest_paths()
            self._controller._view.show_solution(is_perfect=self._controller._generator.perfect, all_paths=paths, tracks=tracks)
            self._controller._generator.reset()
            print("\033c")
        elif self.index == 1:
            self._settings()

    def _run(self):
        while True:
            print("\033c")
            self._print_menu()
            self._get_key()
            if self.input.startswith("\x1b"):
                self._move()
            elif self.input == '\r':
                print("\033c")
                if self.index == 2:
                    break
                self._execute()
