# Main entry point of the A-Maze-ing program.
# This file is the only one called directly from the command line:
#   python3 a_maze_ing.py config.txt
# It reads the config.txt argument, instantiates the main controller
# (MazeController), and delegates all execution logic to it.
# It also handles high-level errors
# (missing argument, file not found) and displays a help message
# to the user in case of incorrect usage.

import sys

try:
    from colorama import Fore, Style
except ImportError:
    print(
        "Error: Colorama not found, try starting the program "
        "with 'make run' command.",
        end="",
    )
    sys.exit(7)
from mazegen import MazeController
try:
    from pydantic import ValidationError
except ImportError:
    print("\033c", end="")
    print(
        "Pydantic not found, try starting the program with 'make run' command."
    )
    sys.exit(7)


def validate_python_environment() -> bool:
    """Ensure the user is in a python virtual environment."""
    if sys.base_prefix != sys.prefix:
        return True
    else:
        print(
            "Warning: You are currently not in a Python virtual environment."
            "\nPlease launch the program with 'make run' command to ensure all"
            " dependencies are installed and available."
        )
        return False


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python3 a_maze_ing.py <config.txt>")
        sys.exit(1)

    try:
        if not validate_python_environment():
            sys.exit(8)
        controller = MazeController(sys.argv[1])
        controller.run()
    except FileNotFoundError as file_error:
        print(f"Error: {file_error}")
        sys.exit(2)
    except PermissionError as perm_error:
        print(f"Error: {perm_error}")
        sys.exit(3)
    except OSError as os_error:
        print(f"Error: {os_error}")
        sys.exit(4)
    except ValidationError as validation_error:
        for error in validation_error.errors():
            print(f" - {error['loc'][0]}: {error['msg']}")
        sys.exit(5)
    except (ValueError, KeyError) as key_error:
        print(f"Error: {key_error}")
        sys.exit(6)
    except KeyboardInterrupt:
        print("\033c")
        print(Fore.BLUE + "Bye-bye" + Style.RESET_ALL, end="")
        print("👋")
        sys.exit(0)


if __name__ == "__main__":
    main()
