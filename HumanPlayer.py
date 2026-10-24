from collections.abc import Callable

from Fleet import Fleet, ShipType
from Grid import Grid
from Player import Player
from console_ui import ask_automatic_placement, ask_target, place_manually


class HumanPlayer(Player):
    """Le joueur humain, en console : il choisit son placement et ses tirs au clavier."""

    def __init__(self, name: str, grid_size: int = Grid.DEFAULT_SIZE, ship_types: tuple[ShipType, ...] = Fleet.CLASSIC,
                 read: Callable[[str], str] = input) -> None:
        super().__init__(name, grid_size, ship_types)
        self.read = read  # source des saisies : le clavier, ou une fonction de test

    def place_fleet(self) -> None:
        if ask_automatic_placement(self.read):
            self.grid.place_randomly(self.fleet)
        else:
            place_manually(self.grid, self.fleet, self.read)

    def choose_target(self, enemy_grid: Grid) -> tuple[int, int]:
        return ask_target(enemy_grid, self.read)
