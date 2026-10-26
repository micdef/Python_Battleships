"""Le joueur humain, qui joue au clavier dans la console."""

from battleships.console_ui import ConsoleUI
from battleships.grid import Grid
from battleships.player import Player
from battleships.rules import CLASSIC_RULES, Rules


class HumanPlayer(Player):
    """Le joueur humain, en console : il choisit son placement et ses tirs au clavier."""

    def __init__(self, name: str, ui: ConsoleUI, rules: Rules = CLASSIC_RULES) -> None:
        """Crée le joueur humain.

        ui est la console par laquelle il voit le jeu et répond aux questions.
        """
        super().__init__(name, rules)
        self._ui = ui

    def place_fleet(self) -> None:
        """Demande au joueur un placement automatique ou manuel, puis l’exécute."""
        if self._ui.ask_automatic_placement():
            self.grid.place_randomly(self.fleet)
        else:
            self._ui.place_manually(self.grid, self.fleet)

    def choose_target(self, enemy_grid: Grid) -> tuple[int, int]:
        """Réaffiche les grilles et les derniers tirs, puis demande au joueur la case à viser."""
        self._ui.refresh_screen(self.grid, self.fleet, enemy_grid)
        return self._ui.ask_target(enemy_grid)
