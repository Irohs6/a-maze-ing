# Main entry point of the A-Maze-ing program.
# This file is the only one called directly from the command line:
#   python3 a_maze_ing.py config.txt
# It reads the config.txt argument, instantiates the main controller
# (MazeController), and delegates all execution logic to it.
# It also handles high-level errors
# (missing argument, file not found) and displays a help message
# to the user in case of incorrect usage.

import sys
from colorama import Fore, Style
from controller.maze_controller import MazeController
from pydantic import ValidationError


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python3 a_maze_ing.py <config.txt>")
        sys.exit(2)

    try:
        controller = MazeController(sys.argv[1])
        controller.run()
    except FileNotFoundError as error:
        print(error)
        sys.exit(1)
    except PermissionError as error:
        print(f"Error: {error}")
        sys.exit(2)
    except OSError as error:
        print(f"Error: {error}")
        sys.exit(3)
    except ValidationError as errors:
        for error in errors.errors():
            print(f" - {error['loc'][0]}: {error['msg']}")
        sys.exit(4)
    except (ValueError, KeyError) as error:
        print(f"Error: {error}")
        sys.exit(5)
    except KeyboardInterrupt:
        print("\033c")
        print(Fore.BLUE + "Bye-bye" + Style.RESET_ALL, end="")
        print("👋")
        sys.exit(0)


if __name__ == "__main__":
    main()
