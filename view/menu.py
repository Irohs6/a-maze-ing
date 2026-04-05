import os
import sys
from colorama import init, Fore, Style

# Initialise Colorama
init()


# ============================================================
#  GESTION MULTIPLATEFORME DES TOUCHES CLAVIER
# ============================================================

if sys.platform.startswith("win"):
    import msvcrt

    def getkey():
        c = msvcrt.getch()
        if c in (b'\x00', b'\xe0'):
            return c + msvcrt.getch()
        return c

else:
    import tty
    import termios

    def getkey():
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            c = sys.stdin.read(1)
            if c == "\x1b":
                c += sys.stdin.read(2)
            return c
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)


# ============================================================
#  CLASSE MENU AVEC CHANGEMENT D'ÉCRAN
# ============================================================

class Menu:
    """
    Menu interactif avec navigation clavier et cadre ASCII.
    Peut ouvrir un nouvel écran dans le même terminal.
    """

    def __init__(self, options, title="Menu", actions=None):
        """
        options : liste des options du menu
        title   : titre affiché
        actions : liste de fonctions à appeler pour chaque option
        """
        self.options = options
        self.title = title
        self.index = 0
        self.actions = actions or [None] * len(options)

    def clear(self):
        os.system("cls" if os.name == "nt" else "clear")

    # --------------------------------------------------------
    # Affichage du menu
    # --------------------------------------------------------
    def _print_menu(self):
        self.clear()

        max_len = max(len(opt) for opt in self.options)
        frame_width = max(max_len, len(self.title)) + 6

        print("╔" + "═" * frame_width + "╗")

        title_padding = (frame_width - len(self.title)) // 2
        print("║" + " " * title_padding + Fore.CYAN + self.title + Style.RESET_ALL +
              " " * (frame_width - len(self.title) - title_padding) + "║")

        print("╠" + "═" * frame_width + "╣")

        for i, opt in enumerate(self.options):
            padding = frame_width - len(opt)
            if i == self.index:
                line = "\033[7m" + Fore.YELLOW + opt + Style.RESET_ALL
            else:
                line = Fore.WHITE + opt + Style.RESET_ALL

            print("║ " + line + " " * (padding - 1) + "║")

        print("╚" + "═" * frame_width + "╝")

    # --------------------------------------------------------
    # Gestion des touches
    # --------------------------------------------------------
    def _handle_key_windows(self, key):
        if key == b'\xe0H':
            self.index = (self.index - 1) % len(self.options)
        elif key == b'\xe0P':
            self.index = (self.index + 1) % len(self.options)
        elif key == b'\r':
            return True
        return False

    def _handle_key_unix(self, key):
        if key == "\x1b[A":
            self.index = (self.index - 1) % len(self.options)
        elif key == "\x1b[B":
            self.index = (self.index + 1) % len(self.options)
        elif key in ("\n", "\r"):
            return True
        return False

    # --------------------------------------------------------
    # Boucle principale
    # --------------------------------------------------------
    def run(self):
        while True:
            self._print_menu()
            key = getkey()

            if key in (b"q", b"Q", "q", "Q"):
                return None

            if isinstance(key, bytes):
                if self._handle_key_windows(key):
                    return self._execute_action()
            else:
                if self._handle_key_unix(key):
                    return self._execute_action()

    # --------------------------------------------------------
    # Exécute l'action associée à l'option
    # --------------------------------------------------------
    def _execute_action(self):
        action = self.actions[self.index]

        if self.options[self.index].lower() == "quitter":
            return None

        if action:
            action()  # Ouvre un nouvel écran dans le même terminal

        return self.index


# ============================================================
#  EXEMPLE D'UTILISATION AVEC NOUVEL ÉCRAN
# ============================================================

def visualiser_labyrinthe():
    os.system("clear")
    print("=== LABYRINTHE GÉNÉRÉ ===\n")
    print("██████████████████████")
    print("█        █           █")
    print("█  ██ ████ ███ ████  █")
    print("█  █       █       █ █")
    print("██████████████████████")
    print("\nAppuie sur Entrée pour revenir au menu...")
    input()


if __name__ == "__main__":
    options = ["Générer un labyrinthe", "Quitter"]
    actions = [visualiser_labyrinthe, None]

    menu = Menu(options, title="A-Maze-Ing", actions=actions)
    menu.run()
