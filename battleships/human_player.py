"""Le joueur humain, qui joue au clavier dans la console."""

from collections.abc import Callable

from battleships.console_ui import ask_automatic_placement, ask_target, place_manually, refresh_screen
from battleships.fleet import Fleet, ShipType
from battleships.grid import Grid
from battleships.player import Player


class HumanPlayer(Player):
    """Le joueur humain, en console : il choisit son placement et ses tirs au clavier."""

    def __init__(
        self,
        name: str,
        grid_size: int = Grid.DEFAULT_SIZE,
        ship_types: tuple[ShipType, ...] = Fleet.CLASSIC,
        read: Callable[[str], str] = input,
    ) -> None:
        """Crée le joueur humain.
        read est la source des saisies (le clavier par défaut, une fausse saisie dans les tests).
        """
        super().__init__(name, grid_size, ship_types)
        self.read = read  # source des saisies : le clavier, ou une fonction de test

    def place_fleet(self) -> None:
        """Demande au joueur un placement automatique ou manuel, puis l’exécute."""
        if ask_automatic_placement(self.read):
            self.grid.place_randomly(self.fleet)
        else:
            place_manually(self.grid, self.fleet, self.read)

    def choose_target(self, enemy_grid: Grid) -> tuple[int, int]:
        """Réaffiche les grilles et les derniers tirs, puis demande au joueur la case à viser."""
        refresh_screen(self.grid, self.fleet, enemy_grid)  # l'humain voit ses deux grilles avant de viser
        return ask_target(enemy_grid, self.read)
