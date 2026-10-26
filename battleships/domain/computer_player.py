"""Le joueur ordinateur."""

import random

from battleships.domain.grid import Grid
from battleships.domain.player import Player


class ComputerPlayer(Player):
    """L'ordinateur : place sa flotte au hasard et tire au hasard sur les cases jamais visées."""

    def place_fleet(self) -> None:
        """Place toute la flotte au hasard."""
        self.grid.place_randomly(self.fleet)

    def choose_target(self, enemy_grid: Grid) -> tuple[int, int]:
        """Tire au hasard parmi les cases jamais visées."""
        # Seul cell.hit est consulté : l'ordinateur ne regarde jamais où sont les bateaux
        candidates = [(cell.row, cell.col) for row in enemy_grid.cells for cell in row if not cell.hit]
        return random.choice(candidates)
